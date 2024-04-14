from discord.ext.pages import Paginator
from discord import Embed

from src.classes.PlayerGameStats import PlayerGameStats
from src.utils import chunks


def leaderboard(stats: dict[str, PlayerGameStats]) -> Paginator:
    leaderboard = sorted(stats.values(), reverse=True, key=lambda x: x.mmr.mu)
    page_list = []
    PAGE_SIZE = 20

    rank = 1
    for rows in chunks(leaderboard, PAGE_SIZE):
        embed = Embed(title=f"Inhouses Leaderboard")
        table_header = (
            f"```{'Rank':5}{'Name':18}{'MMR':6}{'Wins':6}{'Losses':7}{'Winrate':<13}```"
        )
        table_body = "```"
        for row in rows:
            table_body += f"{rank}".ljust(5)
            table_body += f"{row.name.displayName:18}"
            table_body += f"{row.mmr.mu:<6.0f}"
            table_body += f"{row.wins:<6}{row.losses:<7}{row.winrate:>3}%"
            table_body += "\n"
            rank += 1
        table_body += "```"
        embed.add_field(name="", value=table_header + table_body)

        page_list.append(embed)

    paginator = Paginator(
        pages=page_list, loop_pages=True, author_check=False, timeout=None
    )
    return paginator
