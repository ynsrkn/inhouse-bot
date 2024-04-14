from discord import Embed, ApplicationContext, AutocompleteContext
from discord.ext import commands
from discord.ext.pages import Paginator
from discord.commands import option
from discord.utils import basic_autocomplete
import logging
from pymongo.database import Database

from scripts.generate_player_stats import track_player_stats, load_games
from scripts.utils import (
    load_config,
    set_logging_config,
    get_database_connection,
)
from scripts.scrape_match_data import scrape_match_data
from scripts.constants import CONFIG_PATH
from scripts.classes.Match import Match
from scripts.classes.PlayerGameStats import PlayerGameStats
from scripts.classes.ClientNotOpenException import ClientNotOpenException
from scripts.commands.profile import profile
from scripts.commands.leaderboard import leaderboard
from scripts.commands.synergy import synergy
from scripts.commands.versus import versus
from scripts.commands.match_details import match_details

bot = commands.Bot()

# load config
config = load_config(CONFIG_PATH)

GUILD_IDS = config["GUILD_IDS"]

# open local database connection
db: Database = get_database_connection(config["DB_CONNECTION_STRING"])

# stats object
stats: dict[str, PlayerGameStats] = None
# match history
match_history: list[Match] = None
# discord -> riot id mappings
name_mappings: dict[str, tuple[str, str]] = None


async def __get_player_list(ctx: AutocompleteContext):
    """
    Returns a lexicographically sorted list of player display names for autocompleting
    """
    names = list(map(lambda x: x.name, stats.values()))
    names.sort(key=lambda x: x.name)
    display_names = list(map(lambda x: x.displayName, names))
    return display_names


@bot.slash_command(
    name="profile", description="Get a summoners profile.", guild_ids=GUILD_IDS
)
@option("player_name", autocomplete=basic_autocomplete(__get_player_list))
async def cmd_profile(ctx: ApplicationContext, player_name: str = None):

    logging.info(f"Received PROFILE request {player_name=}, author={ctx.author.name}")

    response: Embed | Paginator = profile(
        stats, name_mappings, ctx.author.name, player_name
    )

    if isinstance(response, Embed):
        await ctx.respond(embed=response)
    elif isinstance(response, Paginator):
        await response.respond(ctx.interaction, ephemeral=False)
    else:
        logging.error("Unexpected type returned from profile")


@bot.slash_command(
    name="leaderboard", description="Display leaderboard.", guild_ids=GUILD_IDS
)
async def cmd_leaderboard(ctx: ApplicationContext):

    logging.info(f"Received LEADERBOARD request")

    response: Paginator = leaderboard(stats)

    await response.respond(ctx.interaction)


@bot.slash_command(
    name="synergy",
    description="Get the winrate of two players when on the same team.",
    guild_ids=GUILD_IDS,
)
@option("player1", autocomplete=basic_autocomplete(__get_player_list))
@option("player2", autocomplete=basic_autocomplete(__get_player_list))
async def cmd_synergy(ctx: ApplicationContext, player1: str, player2: str):

    logging.info(f"Received SYNERGY request player1={player1}, player2={player2}")

    response: Embed = synergy(stats, player1, player2)

    await ctx.respond(embed=response)


@bot.slash_command(
    name="versus",
    description="Get the winrate of player1 when against player2.",
    guild_ids=GUILD_IDS,
)
@option("player1", autocomplete=basic_autocomplete(__get_player_list))
@option("player2", autocomplete=basic_autocomplete(__get_player_list))
async def cmd_versus(ctx: ApplicationContext, player1: str, player2: str):

    logging.info(f"Received VERSUS request player1={player1}, player2={player2}")

    response: Embed = versus(stats, player1, player2)

    await ctx.respond(embed=response)


@bot.slash_command(
    name="match_details",
    description="Return a detailed description of a specific match. Returns most recent game if id not specified.",
)
@option("match_id")
async def cmd_match_details(ctx: ApplicationContext, match_id: int = -1):
    logging.info(f"Received MATCH_DETAILS request for match_id: {match_id}")

    response: Embed = match_details(match_history, match_id)

    await ctx.respond(embed=response)


def __update():
    """
    Scrapes custom games from local match history and updates the global
    match_history and stats objects. Requires client to be open
    """
    global match_history, stats

    # scrape custom games from Yunis's PC
    # requires client to be open locally
    logging.info("Scraping client")

    scrape_match_data(db)
    matches = load_games(db)
    stats, predictions = track_player_stats(matches)

    if len(matches) != len(predictions):
        raise Exception("matches and predictions are of different lengths")

    match_history = [Match(matches[i], predictions[i]) for i in range(len(matches))]


@bot.slash_command(name="update", description="Triggers a stats recalc.")
async def cmd_update(ctx: ApplicationContext):
    await ctx.defer(ephemeral=False)

    logging.info("Received UPDATE request")
    try:
        __update()
    except ClientNotOpenException:
        await ctx.respond(
            embed=Embed(
                title="Update Failed: client not open on Yunis' PC. Go beg him"
            ),
            ephemeral=False,
        )
        return

    await ctx.respond(embed=Embed(title="Stats updated!"), ephemeral=False)


@bot.slash_command(
    name="register", description="Register your discord user with a riot id."
)
async def cmd_register(ctx: ApplicationContext, riot_name: str, riot_tag: str):
    await ctx.defer(ephemeral=False)

    logging.info(
        f"Received REGISTER request author={ctx.author.name}, {riot_name=}, {riot_tag=}"
    )

    # strip leading # in case users input it with their tag
    if len(riot_tag) > 0 and riot_tag[0] == "#":
        riot_tag = riot_tag[1:]

    # validate name and tag
    if (
        len(riot_name) < 3
        or len(riot_name) > 16
        or len(riot_tag) < 3
        or len(riot_tag) > 5
    ):
        await ctx.respond(
            embed=Embed(
                title=(
                    "Register failed: Invalid name or tag. Names must  \
                       be between 3 and 16 characters, tags between 3 and 5."
                )
            )
        )
        return

    mapping = {
        "discord_name": ctx.author.name,
        "riot_name": riot_name,
        "riot_tag": riot_tag,
    }

    db["discord-riot-id-mappings"].replace_one(
        filter={"discord_name": ctx.author.name}, replacement=mapping, upsert=True
    )

    global name_mappings

    name_mappings[ctx.author.name] = (riot_name, riot_tag)

    await ctx.respond(
        embed=Embed(
            title=f"Successfully registered {ctx.author.name} as {riot_name}#{riot_tag}"
        )
    )


def __fetch_name_mappings(db: Database) -> dict[str, tuple[str, str]]:
    """
    Pull discord username -> riot id + tagline mappings from mongoDB database and return a dict of them.
    Discord usernames are guaranteed at the database level to be unique.
    """
    mappings = {}

    query_results = db["discord-riot-id-mappings"].find()
    for mapping in query_results:
        mappings[mapping["discord_name"]] = (mapping["riot_name"], mapping["riot_tag"])

    return mappings


"""
    App entry point
"""
if __name__ == "__main__":

    # Set log level
    set_logging_config()

    # initialize stats object on startup
    try:
        logging.info("Calculating stats and match history")
        __update()
    except ClientNotOpenException:
        logging.info("Client not open")

    # get discord -> riot id mappings from db
    name_mappings = __fetch_name_mappings(db)  # global

    logging.info("Populated objects; Ready!")

    bot.run(config["DISCORD_TOKEN"])
