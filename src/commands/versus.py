from discord import Embed

from src.classes.PlayerGameStats import PlayerGameStats


def versus(stats: dict[str, PlayerGameStats], player1: str, player2: str) -> Embed:
    player1_key = player1.lower()
    player2_key = player2.lower()

    p_stats = stats.get(player1_key)
    if p_stats is None:
        return Embed(title=f"Couldn't find {player1}.")

    versus = p_stats.opponents.get(player2_key)
    if versus is None:
        return Embed(
            title=f"Either {player1} has not played any games against {player2} or their name was mistyped."
        )

    embed = Embed(
        title=f"Versus between `{p_stats.name.displayName}` and `{versus.name.displayName}`"
    )

    body = ""
    body += f"Thats {abs(p_stats.winrate - versus.winrate)}% {'higher' if versus.winrate >= p_stats.winrate else 'lower'} than normal.\n"
    body += f"**{versus.wins}W {versus.losses}L**"
    embed.add_field(
        name=f"`{p_stats.name.displayName}` wins `{versus.winrate}%` of the time when playing against `{versus.name.displayName}`.",
        value=body,
        inline=False,
    )

    return embed
