from generate_player_stats import track_player_stats, load_games
from constants import MATCHES_PATH, SECRETS_PATH
from utils import chunks
from scrape_match_data import scrape_match_data

from classes.Match import Match
from classes.Game import Game
from classes.PlayerGameStats import PlayerGameStats
from classes.PlayerHistoricalStats import PlayerHistoricalStats
from classes.Teammate import Teammate
from classes.ChampionStats import ChampionStats
from classes.ClientNotOpenException import ClientNotOpenException

import discord
from discord.ext import commands, pages
from discord.commands import option
from discord.utils import basic_autocomplete
import logging
import json

bot = commands.Bot()
#            Test server          Monkeys             Free Isreal
GUILD_IDS = [1216905929350582312, 317463653597052928, 695069672705359953]

# Set log level
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# stats object
stats: dict[PlayerGameStats] = None
# match history
match_history: list[Match] = None

async def __get_player_list(ctx: discord.AutocompleteContext):
    """
        Returns a lexicographically sorted list of player display names for autocompleting
    """
    return sorted(list(map(lambda x: x.playerDisplayName, stats.values())))

@bot.slash_command(
    name="profile",
    description="Get a summoners profile.",
    guild_ids=GUILD_IDS
)
@option("player_name", autocomplete=basic_autocomplete(__get_player_list))
async def get_profile(
        ctx: discord.ApplicationContext,
        player_name: str
    ):

    logging.info(f"Received PROFILE request player_name={player_name}")

    p_stats = stats.get(player_name.lower())
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player_name}"))
        return

    MIN_EMBED_WIDTH = 48
    profile_embed = discord.Embed(
        title=f"{p_stats.playerDisplayName} Profile",
        description="⎯" * MIN_EMBED_WIDTH
    )

    profile_embed.add_field(
        name=f"**{p_stats.mmr.mu:.0f} MMR**\n",            
        value=f"{p_stats.wins}W {p_stats.losses}L {p_stats.winrate}% WR",
        inline=True
    )
    profile_embed.add_field(
        name="KDA",
        value=f"{p_stats.avgKills} / {p_stats.avgDeaths} / {p_stats.avgAssists} ({p_stats.totalkda})",
        inline=True
    )
    # empty field for spacing
    profile_embed.add_field(name="", value="", inline=False)

    profile_embed.add_field(
        name="CS/min",
        value=f"{p_stats.csPerMin}",
        inline=True
    )
    profile_embed.add_field(
        name="Average Damage Dealt",
        value=f"{p_stats.averageDamageDealt:,}",
        inline=True
    )

    # Champion stats

    # determines sorting order for top champion stats
    def champStatsComparison(stats: ChampionStats):
        return (stats.gamesPlayed, stats.winrate, stats.avgkda)
    
    top_champs = sorted(p_stats.championStats.values(), key=champStatsComparison, reverse=True)
    
    PAGE_SIZE = 5
    champions_pages = []
    rank = 1
    for chunk in chunks(top_champs, PAGE_SIZE):
        champions_embed = discord.Embed(
            title="Champion Stats",
            description="⎯" * MIN_EMBED_WIDTH
        )

        body = "```"
        for champ in chunk:
            body += f"{rank}. {champ.championName}".ljust(18)
            body += f"{champ.avgkda} KDA".ljust(13)
            body += f"{champ.winrate}% WR".rjust(8)
            body += "\n"
            # next line
            body += " " * 16 # spacer
            body += f"{champ.avgKills}/{champ.avgDeaths}/{champ.avgAssists}".ljust(15)
            body += f"{champ.gamesPlayed} game{'s' if champ.gamesPlayed > 1 else ''}".rjust(8)
            body += "\n"
            rank += 1
        body += "```"

        champions_embed.add_field(
            name=f"",
            value=body,
            inline=False
        )

        champions_pages.append(champions_embed)

    # Player Match History

    PAGE_SIZE = 20
    match_hist_pages = []
    for i, chunk in enumerate(chunks(p_stats.matchHistory, PAGE_SIZE)):
        page_embed = discord.Embed(
            title="Match History",
            description="⎯" * MIN_EMBED_WIDTH
        )
        table_header = f"```{'ID':5}{'Result':10}{'Champion':13}{'KDA':10}{'MMR ±':11}```"
        body = "```"
        for match in chunk:
            matchStats = match.gameStats
            body += str(matchStats.gameId).ljust(5)
            body += f"{'Victory' if matchStats.win else 'Defeat':10}"
            body += f"{matchStats.championName:13}"
            body += f"{matchStats.kills}/{matchStats.deaths}/{matchStats.assists}".ljust(10)
            body += f"{'+' if match.mmrDelta >= 0 else ''}{match.mmrDelta:.0f}".ljust(6)
            body += "\n"
        body += "```"

        page_embed.add_field(name="", value=table_header + body, inline=False)

        match_hist_pages.append(page_embed)
    
    page_list = []
    for i in range(max(len(champions_pages), len(match_hist_pages))):
        pg = [profile_embed]
        if i < len(champions_pages):
            pg.append(champions_pages[i])
        else:
            pg.append(champions_pages[-1])
        if i < len(match_hist_pages):
            pg.append(match_hist_pages[i])
        else:
            pg.append(match_hist_pages[-1])
        page_list.append(pg)

    paginator = pages.Paginator(pages=page_list, loop_pages=True, author_check=False, timeout=None)
    await paginator.respond(ctx.interaction, ephemeral=False)


@bot.slash_command(
    name="leaderboard",
    description="Display leaderboard.",
    guild_ids=GUILD_IDS
)
async def get_leaderboard(
        ctx: discord.ApplicationContext
    ):

    logging.info(f"Received LEADERBOARD request")

    leaderboard = sorted(stats.values(), reverse=True, key=lambda x: x.mmr.mu)
    page_list = []
    PAGE_SIZE = 20

    rank = 1
    for rows in chunks(leaderboard, PAGE_SIZE):
        embed = discord.Embed(
            title=f"Inhouses Leaderboard"
        )
        table_header = f"```{'Rank':5}{'Name':18}{'MMR':6}{'Wins':6}{'Losses':7}{'Winrate':<13}```"
        table_body = "```"
        for row in rows:
            table_body += f"{rank}".ljust(5)
            table_body += f"{row.playerDisplayName:18}"
            table_body += f"{row.mmr.mu:<6.0f}"
            table_body += f"{row.wins:<6}{row.losses:<7}{row.winrate:>3}%"
            table_body += "\n"
            rank += 1
        table_body += '```'
        embed.add_field(name="", value=table_header + table_body)
        
        page_list.append(embed)

    paginator = pages.Paginator(pages=page_list, loop_pages=True, author_check=False, timeout=None)
    await paginator.respond(ctx.interaction)


@bot.slash_command(
    name="synergy",
    description="Get the winrate of two players when on the same team.",
    guild_ids=GUILD_IDS
)
@option("player1", autocomplete=basic_autocomplete(__get_player_list))
@option("player2", autocomplete=basic_autocomplete(__get_player_list))
async def get_synergy(
        ctx: discord.ApplicationContext,
        player1: str,
        player2: str
    ):

    logging.info(f"Received SYNERGY request player1={player1}, player2={player2}")

    player1_key = player1.lower()
    player2_key = player2.lower()
    
    p_stats = stats.get(player1_key)
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player1}."))
        return
    p2_stats = stats.get(player2_key)
    if p2_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player2}."))
        return
    
    synergy = p_stats.teammates.get(player2_key)
    if synergy is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player1} has not played any games with {player2} or their name was mistyped."))
        return
    p2_synergy = p2_stats.teammates.get(player1_key)
    if synergy is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player2} has not played any games with {player1} or their name was mistyped."))
        return

    embed = discord.Embed(
        title=f"Synergy between `{p_stats.playerDisplayName}` and `{p2_stats.playerDisplayName}`"
    )

    body = ""
    body += f"Thats **{abs(p_stats.winrate - synergy.winrate)}% {'higher' if synergy.winrate >= p_stats.winrate else 'lower'}** than normal for `{p_stats.playerDisplayName}` "
    body += f"and **{abs(p2_stats.winrate - p2_synergy.winrate)}% {'higher' if p2_synergy.winrate >= p2_stats.winrate else 'lower'}** than normal for `{p2_stats.playerDisplayName}`.\n"
    body += f"**{synergy.wins}W {synergy.losses}L**"
    embed.add_field(
        name=f"`{p_stats.playerDisplayName}` wins `{synergy.winrate}%` of the time when playing with `{p2_stats.playerDisplayName}`.",
        value=body,
        inline=False
    )

    await ctx.respond(embed=embed)


@bot.slash_command(
    name="versus",
    description="Get the winrate of player1 when against player2.",
    guild_ids=GUILD_IDS
)
@option("player1", autocomplete=basic_autocomplete(__get_player_list))
@option("player2", autocomplete=basic_autocomplete(__get_player_list))
async def get_versus(
        ctx: discord.ApplicationContext,
        player1: str,
        player2: str
    ):

    logging.info(f"Received VERSUS request player1={player1}, player2={player2}")

    player1_key = player1.lower()
    player2_key = player2.lower()

    p_stats = stats.get(player1_key)
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player1}."))
        return
    
    versus = p_stats.opponents.get(player2_key)
    if versus is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player1} has not played any games against {player2} or their name was mistyped."))
        return

    embed = discord.Embed(
        title=f"Versus between `{p_stats.playerDisplayName}` and `{versus.playerDisplayName}`"
    )

    body = ""
    body += f"Thats {abs(p_stats.winrate - versus.winrate)}% {'higher' if versus.winrate >= p_stats.winrate else 'lower'} than normal.\n"
    body += f"**{versus.wins}W {versus.losses}L**"
    embed.add_field(
        name=f"`{p_stats.playerDisplayName}` wins `{versus.winrate}%` of the time when playing against `{versus.playerDisplayName}`.",
        value=body,
        inline=False
    )

    await ctx.respond(embed=embed)


@bot.slash_command(
    name="match_details",
    description="Return a detailed description of a specific match. Returns most recent game if id not specified."
)
async def match_details(ctx, match_id: discord.Option(int) = -1):
    logging.info(f"Received MATCH_DETAILS request for match_id: {match_id}")

    # if match_id is not specified return most recent game
    if match_id == -1:
        match_id = len(match_history)
    
    if match_id > len(match_history):
        await ctx.respond(embed=discord.Embed(title=f"Could not find match #{match_id}"))
        return
    
    match_info = match_history[match_id - 1].game
    match_prediction = match_history[match_id - 1].prediction * 100
    game_min, game_sec = divmod(match_info.gameDuration, 60)
    embed = discord.Embed(
        title=f"Match Details For Match #{match_id}"
    )

    result_header = f"{match_info.result} in {game_min:02d}:{game_sec:02d}".ljust(62)
    result_header += f"{match_prediction:.2f}% Blue vs {100 - match_prediction:.2f}% Red"
    table_header = f"```{'Name':16}{'Champion':13}{'KDA':10}{'CS':6}{'DMG':12}```"
    embed.add_field(name=result_header, value=table_header, inline=False)

    for name, team in [("BLUE", match_info.team1), ("RED", match_info.team2)]:
        body = "```"
        for player in team:
            body += f"{player.playerDisplayName:16}"
            body += f"{player.championName:13}"
            body += f"{player.kills}/{player.deaths}/{player.assists}".ljust(10)
            body += f"{player.cs:<6}"
            body += f"{player.damageDealt / 1000:,.1f}k"
            body += "\n"
        body += "```"
        embed.add_field(name=f"**{name}**", value=body, inline=False)

    await ctx.respond(embed=embed)


def __update():
    """
        Scrapes custom games from local match history and updates the global
        match_history and stats objects. Requires client to be open
    """
    global match_history, stats

    # scrape custom games from Yunis's PC
    # requires client to be open locally
    logging.info("Scraping client")
    try:
        scrape_match_data()
    finally:
        matches = load_games(MATCHES_PATH)
        stats, predictions = track_player_stats(matches)

        if len(matches) != len(predictions):
            raise Exception("matches and predictions are of different lengths")
        
        match_history = [Match(matches[i], predictions[i]) for i in range(len(matches))]

@bot.slash_command(
    name="update",
    description="Triggers a stats recalc."
)
async def update(ctx):
    await ctx.defer(ephemeral=False)

    logging.info("Received UPDATE request")
    try:
        __update()
    except ClientNotOpenException:
        await ctx.respond(
            embed=discord.Embed(title="Update Failed: client not open on Yunis' PC. Go beg him"),
            ephemeral=False
        )
        return
    
    await ctx.respond(embed=discord.Embed(title="Stats updated!"), ephemeral=False)

"""
    App entry point
"""
if __name__ == "__main__":
    # initialize stats object on startup
    logging.info("Calculating stats and match history")
    try:
        __update()
    except ClientNotOpenException:
        logging.info("Client not open")

    logging.info("Populated objects; Ready!")

    with open(SECRETS_PATH) as fh:
        secrets = json.load(fh)
        token = secrets['token']


    bot.run(token)
