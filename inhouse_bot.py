import discord
from discord.ext import commands
from generate_player_stats import track_player_stats, load_games
import logging
import json

bot = commands.Bot()
#            Test server          Monkeys             Free Isreal
GUILD_IDS = [1216905929350582312, 317463653597052928, 695069672705359953]

# Set log level
logging.basicConfig(level=logging.INFO)

# stats object
stats = None
# match history
match_history = None

@bot.slash_command(
    name="profile",
    description="Get a summoners profile.",
    guild_ids=GUILD_IDS
)
async def get_profile(ctx, player_name: str):
    logging.info(f"Received PROFILE request player_name={player_name}")

    p_stats = stats.get(player_name)
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title="Couldn't find {player_name}"))
        return

    embed = discord.Embed(
        title=f"{player_name} Profile",
    )

    embed.add_field(
        name=f"**{p_stats.wins}W {p_stats.losses}L**\n",            
        value=f"{p_stats.winrate}% Win Rate",
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

    table_header = f"```{'ID':5}{'Result':10}{'Champion':13}{'KDA':8}```"
    body = "```"
    for match in p_stats.matchHistory[:20]:
        body += str(match.gameId).ljust(5)
        body += f"{'Victory' if match.win else 'Defeat':10}"
        body += f"{match.championName:13}"
        body += f"{match.kills}/{match.deaths}/{match.assists}"
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
    table_header = f"```{'Rank':5}{'Name':18}{'Wins':6}{'Losses':7}{'Winrate':<7}```"
    table_body = "```"
    rows = sorted(stats.values(), reverse=True, key=lambda x: (x.wins - x.losses, x.gamesPlayed, x.winrate))
    for i, row in enumerate(rows):
        table_body += f"{i + 1}".ljust(5)
        table_body += f"{row.playerName:18}"
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

    p_stats = stats.get(player1)
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player1}."))
        return
    p2_stats = stats.get(player2)
    if p2_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player2}."))
        return
    
    synergy = p_stats.teammates.get(player2)
    if synergy is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player1} has not played any games with {player2} or their name was mistyped."))
        return
    p2_synergy = p2_stats.teammates.get(player1)
    if synergy is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player2} has not played any games with {player1} or their name was mistyped."))
        return

    embed = discord.Embed(
        title=f"Synergy between `{player1}` and `{player2}`"
    )

    body = ""
    body += f"Thats **{abs(p_stats.winrate - synergy.winrate)}% {'higher' if synergy.winrate >= p_stats.winrate else 'lower'}** than normal for `{player1}` "
    body += f"and **{abs(p2_stats.winrate - p2_synergy.winrate)}% {'higher' if p2_synergy.winrate >= p2_stats.winrate else 'lower'}** than normal for `{player2}`.\n"
    body += f"**{synergy.wins}W {synergy.losses}L**"
    embed.add_field(
        name=f"`{player1}` wins `{synergy.winrate}%` of the time when playing with `{player2}`.",
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

    p_stats = stats.get(player1)
    if p_stats is None:
        await ctx.respond(embed=discord.Embed(title=f"Couldn't find {player1}."))
        return
    
    versus = p_stats.opponents.get(player2)
    if versus is None:
        await ctx.respond(embed=discord.Embed(title=f"Either {player1} has not played any games against {player2} or their name was mistyped."))
        return

    embed = discord.Embed(
        title=f"Versus between `{player1}` and `{player2}`"
    )

    body = ""
    body += f"Thats {abs(p_stats.winrate - versus.winrate)}% {'higher' if versus.winrate >= p_stats.winrate else 'lower'} than normal.\n"
    body += f"**{versus.wins}W {versus.losses}L**"
    embed.add_field(
        name=f"`{player1}` wins `{versus.winrate}%` of the time when playing against `{player2}`.",
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
    
    match_info = match_history[match_id - 1]
    game_min, game_sec = divmod(match_info.gameDuration, 60)
    embed = discord.Embed(
        title=f"Match Details For Match #{match_id}"
    )

    header = f"```{'Name':16}{'Champion':13}{'KDA':10}{'CS':6}{'DMG':8}```"
    embed.add_field(name=f"{match_info.result} in {game_min:02d}:{game_sec:02d}", value=header, inline=False)

    for name, team in [("BLUE", match_info.team1), ("RED", match_info.team2)]:
        body = "```"
        for player in team:
            body += f"{player.playerName:16}"
            body += f"{player.championName:13}"
            body += f"{player.kills}/{player.deaths}/{player.assists}".ljust(10)
            body += f"{player.cs:<6}"
            body += f"{player.damageDealt:,}"
            body += "\n"
        body += "```"
        embed.add_field(name=f"**{name}**", value=body, inline=False)

    await ctx.respond(embed=embed)

@bot.slash_command(
    name="update",
    description="Triggers a stats recalc."
)
async def update(ctx):
    logging.info("Received UPDATE request")

    match_history = load_games("matches/")
    stats = track_player_stats(match_history)
    await ctx.respond(embed=discord.Embed(title="Stats updated!"))

if __name__ == "__main__":
    # initialize stats object on startup
    logging.info("Calculating stats and match history")
    match_history = load_games("matches/")
    stats = track_player_stats(match_history)
    logging.info("Populated objects; Ready!")

    with open("secrets.json") as fh:
        token = json.load(fh)['token']

    bot.run(token)