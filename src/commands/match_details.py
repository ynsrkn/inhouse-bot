from discord import Embed

from src.classes.Match import Match


def match_details(match_history: list[Match], match_id: int) -> Embed:
    # if match_id is not specified return most recent game
    if match_id == -1:
        match_id = len(match_history)

    if match_id > len(match_history):
        return Embed(title=f"Could not find match #{match_id}")

    match_info = match_history[match_id - 1].game
    match_prediction = match_history[match_id - 1].prediction * 100
    game_min, game_sec = divmod(match_info.gameDuration, 60)
    embed = Embed(title=f"Match Details For Match #{match_id}")

    result_header = f"{match_info.result} in {game_min:02d}:{game_sec:02d}".ljust(62)
    result_header += (
        f"{match_prediction:.2f}% Blue vs {100 - match_prediction:.2f}% Red"
    )
    table_header = f"```{'Name':16}{'Champion':13}{'KDA':10}{'CS':6}{'DMG':12}```"
    embed.add_field(name=result_header, value=table_header, inline=False)

    for name, team in [("BLUE", match_info.team1), ("RED", match_info.team2)]:
        body = "```"
        for player in team:
            body += f"{player.name.displayName:16}"
            body += f"{player.championName:13}"
            body += f"{player.kills}/{player.deaths}/{player.assists}".ljust(10)
            body += f"{player.cs:<6}"
            body += f"{player.damageDealt / 1000:,.1f}k"
            body += "\n"
        body += "```"
        embed.add_field(name=f"**{name}**", value=body, inline=False)

    return embed
