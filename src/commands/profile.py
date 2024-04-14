from discord import Embed
from discord.ext.pages import Paginator

from src.classes.ChampionStats import ChampionStats
from src.classes.PlayerGameStats import PlayerGameStats
from src.utils import chunks


def profile(
    stats: dict[str, PlayerGameStats],
    name_mappings: dict[str, tuple[str, str]],
    discord_author: str,
    player_name: str,
) -> Embed | Paginator:

    # player_name is optional if a discord -> riot id mapping exists
    if player_name is None:
        riot_id = name_mappings.get(discord_author)
        if riot_id is None:
            return Embed(
                title=(
                    f"{discord_author} does not have a corresponding Riot Id attached. \
                        Specify the player_name field or use the /register command and try again."
                )
            )
        player_name = riot_id[0]

    p_stats = stats.get(player_name.lower())
    if p_stats is None:
        return Embed(title=f"Couldn't find {player_name}")

    MIN_EMBED_WIDTH = 48
    profile_embed = Embed(
        title=f"{p_stats.name.displayName} Profile", description="⎯" * MIN_EMBED_WIDTH
    )

    profile_embed.add_field(
        name=f"**{p_stats.mmr.mu:.0f} MMR**\n",
        value=f"{p_stats.wins}W {p_stats.losses}L {p_stats.winrate}% WR",
        inline=True,
    )
    profile_embed.add_field(
        name="KDA",
        value=f"{p_stats.avgKills} / {p_stats.avgDeaths} / {p_stats.avgAssists} ({p_stats.totalkda})",
        inline=True,
    )
    # empty field for spacing
    profile_embed.add_field(name="", value="", inline=False)

    profile_embed.add_field(name="CS/min", value=f"{p_stats.csPerMin}", inline=True)
    profile_embed.add_field(
        name="Average Damage Dealt",
        value=f"{p_stats.averageDamageDealt:,}",
        inline=True,
    )

    # Champion stats

    # determines sorting order for top champion stats
    def champStatsComparison(stats: ChampionStats):
        return (stats.gamesPlayed, stats.winrate, stats.avgkda)

    top_champs = sorted(
        p_stats.championStats.values(), key=champStatsComparison, reverse=True
    )

    PAGE_SIZE = 5
    champions_pages = []
    rank = 1
    for chunk in chunks(top_champs, PAGE_SIZE):
        champions_embed = Embed(
            title="Champion Stats", description="⎯" * MIN_EMBED_WIDTH
        )

        body = "```"
        for champ in chunk:
            body += f"{rank}. {champ.championName}".ljust(18)
            body += f"{champ.avgkda} KDA".ljust(13)
            body += f"{champ.winrate}% WR".rjust(8)
            body += "\n"
            # next line
            body += " " * 16  # spacer
            body += f"{champ.avgKills}/{champ.avgDeaths}/{champ.avgAssists}".ljust(15)
            plural = "s" if champ.gamesPlayed > 1 else ""
            body += f"{champ.gamesPlayed} game{plural}".rjust(8)
            body += "\n"
            rank += 1
        body += "```"

        champions_embed.add_field(name=f"", value=body, inline=False)

        champions_pages.append(champions_embed)

    # Player Match History

    PAGE_SIZE = 12
    match_hist_pages = []
    for i, chunk in enumerate(chunks(p_stats.matchHistory, PAGE_SIZE)):
        page_embed = Embed(title="Match History", description="⎯" * MIN_EMBED_WIDTH)
        table_header = (
            f"```{'ID':5}{'Result':10}{'Champion':13}{'KDA':10}{'MMR ±':11}```"
        )
        body = "```"
        for match in chunk:
            mstats = match.gameStats
            body += str(mstats.gameId).ljust(5)
            body += f"{'Victory' if mstats.win else 'Defeat':10}"
            body += f"{mstats.championName:13}"
            body += f"{mstats.kills}/{mstats.deaths}/{mstats.assists}".ljust(10)
            body += f"{'+' if match.mmrDelta >= 0 else ''}{match.mmrDelta:.0f}".ljust(6)
            body += "\n"
        body += "```"

        page_embed.add_field(name="", value=table_header + body, inline=False)

        match_hist_pages.append(page_embed)

    page_list = []
    # display pages equal to the max between champions and match history
    # and show the last page of the shorter list
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

    paginator = Paginator(
        pages=page_list, loop_pages=True, author_check=False, timeout=None
    )

    return paginator
