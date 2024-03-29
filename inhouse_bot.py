import discord
from discord.ext import commands
from generate_player_stats import Game, PlayerGameStats, PlayerHistoricalStats, Teammate, ChampionStats
from generate_player_stats import track_player_stats, load_games
import logging
import json

from Match import Match

bot = commands.Bot()
#            Test server          Monkeys             Free Isreal
GUILD_IDS = [1216905929350582312, 317463653597052928, 695069672705359953]

# Set log level
logging.basicConfig(level=logging.INFO)

# stats object
stats: dict[PlayerGameStats] = None
# match history
match_history: list[Match] = None

@bot.slash_command(
    name="profile",
    description="Get a summoners profile.",
    guild_ids=GUILD_IDS
)
async def get_profile(ctx, player_name: str):
    logging.info(f"Received PROFILE request player_name={player_name}")

    p_stats = stats.get(player_name.lower())
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player_name}"))
        return

    embed = discord.Embed(
        title=f"{p_stats.playerDisplayName} Profile",
    )

    embed.add_field(
        name=f"**{p_stats.mmr.mu:.0f} MMR**\n",            
        value=f"{p_stats.wins}W {p_stats.losses}L {p_stats.winrate}% WR",
        inline=True
    )
    embed.add_field(
        name="KDA",
        value=f"{p_stats.avgKills} / {p_stats.avgDeaths} / {p_stats.avgAssists} ({p_stats.totalkda})",
        inline=True
    )
    # empty field for spacing
    embed.add_field(name="", value="", inline=False)

    embed.add_field(
        name="CS/min",
        value=f"{p_stats.csPerMin}",
        inline=True
    )
    embed.add_field(
        name="Average Damage Dealt",
        value=f"{p_stats.averageDamageDealt:,}",
        inline=True
    )

    # Champion stats    
    DISPLAY_NUMBER = 5

    # determines sorting order for top champion stats
    def champStatsComparison(stats: ChampionStats):
        return (stats.gamesPlayed, stats.winrate, stats.avgkda)
    
    top_champs = sorted(p_stats.championStats.values(), key=champStatsComparison, reverse=True)
    body = "```"
    for i, champ in enumerate(top_champs[:DISPLAY_NUMBER]):
        body += f"{i + 1}. {champ.championName}".ljust(18)
        body += f"{champ.avgkda} KDA".ljust(13)
        body += f"{champ.winrate}% WR".rjust(8)
        body += "\n"
        # next line
        body += " " * 16 # spacer
        body += f"{champ.avgKills}/{champ.avgDeaths}/{champ.avgAssists}".ljust(15)
        body += f"{champ.gamesPlayed} game{'s' if champ.gamesPlayed > 1 else ''}".rjust(8)
        body += "\n"
    body += "```"

    embed.add_field(
        name=f"**Champion Stats (Top {DISPLAY_NUMBER})**",
        value=body,
        inline=False
    )

    table_header = f"```{'ID':5}{'Result':10}{'Champion':13}{'KDA':10}{'MMR ±':6}```"
    body = "```"
    for match in p_stats.matchHistory[:20]:
        matchStats = match.gameStats
        body += str(matchStats.gameId).ljust(5)
        body += f"{'Victory' if matchStats.win else 'Defeat':10}"
        body += f"{matchStats.championName:13}"
        body += f"{matchStats.kills}/{matchStats.deaths}/{matchStats.assists}".ljust(10)
        body += f"{'+' if match.mmrDelta >= 0 else ''}{match.mmrDelta:.0f}".ljust(6)
        body += "\n"
    body += "```"
    embed.add_field(name="**Match History:**", value=table_header + body, inline=False)

    await ctx.respond(embed=embed)

@bot.slash_command(
    name="leaderboard",
    description="Display leaderboard.",
    guild_ids=GUILD_IDS
)
async def get_leaderboard(ctx):
    logging.info(f"Received LEADERBOARD request")

    embed = discord.Embed(
        title=f"Inhouses Leaderboard"
    )
    table_header = f"```{'Rank':5}{'Name':18}{'MMR':6}{'Wins':6}{'Losses':7}{'Winrate':<7}```"
    table_body = "```"
    rows = sorted(stats.values(), reverse=True, key=lambda x: x.mmr.mu)
    rows = filter(lambda x: x.gamesPlayed >= 7, rows)
    for i, row in enumerate(rows):
        table_body += f"{i + 1}".ljust(5)
        table_body += f"{row.playerDisplayName:18}"
        table_body += f"{row.mmr.mu:<6.0f}"
        table_body += f"{row.wins:<6}{row.losses:<7}{row.winrate:>3}%"
        table_body += "\n"
    table_body += '```'
    embed.add_field(name="", value=table_header + table_body)

    await ctx.respond(embed=embed)

@bot.slash_command(
    name="synergy",
    description="Get the winrate of two players when on the same team.",
    guild_ids=GUILD_IDS
)
async def get_synergy(ctx, player1: str, player2: str):
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
async def get_versus(ctx, player1: str, player2: str):
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
    description="Return a detailed description of a specific match."
)
async def match_details(ctx, match_id: int):
    logging.info(f"Received MATCH_DETAILS request for match_id: {match_id}")

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
    table_header = f"```{'Name':16}{'Champion':13}{'KDA':10}{'CS':6}{'DMG':8}```"
    embed.add_field(name=result_header, value=table_header, inline=False)

    for name, team in [("BLUE", match_info.team1), ("RED", match_info.team2)]:
        body = "```"
        for player in team:
            body += f"{player.playerDisplayName:16}"
            body += f"{player.championName:13}"
            body += f"{player.kills}/{player.deaths}/{player.assists}".ljust(10)
            body += f"{player.cs:<6}"
            body += f"{player.damageDealt:,}"
            body += "\n"
        body += "```"
        embed.add_field(name=f"**{name}**", value=body, inline=False)

    await ctx.respond(embed=embed)

def __update():
    global match_history, stats

    matches = load_games("matches/")
    stats, predictions = track_player_stats(matches)

    if len(matches) != len(predictions):
        raise Exception("matches and predictions are of different lengths")
    
    match_history = [Match(matches[i], predictions[i]) for i in range(len(matches))]

@bot.slash_command(
    name="update",
    description="Triggers a stats recalc."
)
async def update(ctx):
    logging.info("Received UPDATE request")
    __update()
    await ctx.respond(embed=discord.Embed(title="Stats updated!"))

if __name__ == "__main__":
    # initialize stats object on startup
    logging.info("Calculating stats and match history")
    __update()
    logging.info("Populated objects; Ready!")

    with open("secrets.json") as fh:
        token = json.load(fh)['token']

    bot.run(token)