from discord import Embed

from src.classes.PlayerGameStats import PlayerGameStats


def synergy(stats: dict[str, PlayerGameStats], player1: str, player2: str) -> Embed:
    player1_key = player1.lower()
    player2_key = player2.lower()

    p_stats = stats.get(player1_key)
    if p_stats is None:
        return Embed(title=f"Couldn't find {player1}.")

    p2_stats = stats.get(player2_key)
    if p2_stats is None:
        return Embed(title=f"Couldn't find {player2}.")

    synergy = p_stats.teammates.get(player2_key)
    if synergy is None:
        return Embed(
            title=f"Either {player1} has not played any games with {player2} or their name was mistyped."
        )
    p2_synergy = p2_stats.teammates.get(player1_key)
    if synergy is None:
        return Embed(
            title=f"Either {player2} has not played any games with {player1} or their name was mistyped."
        )

    embed = Embed(
        title=f"Synergy between `{p_stats.name.displayName}` and `{p2_stats.name.displayName}`"
    )

    body = ""

    higher_lower = "higher" if synergy.winrate >= p_stats.winrate else "lower"
    body += f"Thats **{abs(p_stats.winrate - synergy.winrate)}% {higher_lower}** than normal for `{p_stats.name.displayName}` "

    higher_lower = "higher" if p2_synergy.winrate >= p2_stats.winrate else "lower"
    body += f"and **{abs(p2_stats.winrate - p2_synergy.winrate)}% {higher_lower}** than normal for `{p2_stats.name.displayName}`.\n"

    body += f"**{synergy.wins}W {synergy.losses}L**"
    embed.add_field(
        name=f"`{p_stats.name.displayName}` wins `{synergy.winrate}%` of the time when playing with `{p2_stats.name.displayName}`.",
        value=body,
        inline=False,
    )

    return embed
