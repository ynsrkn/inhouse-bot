import itertools
import math
import trueskill
from pymongo.database import Database

from constants import CONFIG_PATH
from classes.PlayerGameStats import PlayerGameStats
from classes.PlayerHistoricalStats import PlayerHistoricalStats
from classes.Game import Game
from utils import load_config, get_database_connection


# setup trueskill global environment
MU = 1200
DRAW_PROB = 0
BETA = 500
SIGMA = 400
trueskill.setup(mu=MU, draw_probability=DRAW_PROB, sigma=SIGMA, beta=BETA)


def __calculate_win_probability(rating_groups) -> float:
    """
    Calculate win probablility between two teams in Trueskill
    """
    team1 = rating_groups[0].values()
    team2 = rating_groups[1].values()
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma**2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)


def track_player_stats(
    games: list[Game],
) -> tuple[dict[str, PlayerHistoricalStats], list[float]]:
    """
    Iterates through a list of games and generates overall stats for each player
    as well as predictions for each game
    """
    player_stats: dict[str, PlayerHistoricalStats] = {}
    game_predictions: list[float] = []

    def __get_team_mmrs(team: list[PlayerGameStats]):
        team_mmrs = {}
        for player_game_stats in team:
            player_name = player_game_stats.playerName
            playerDisplayName = player_game_stats.playerDisplayName

            if player_name not in player_stats:
                player_stats[player_name] = PlayerHistoricalStats(
                    player_name, playerDisplayName
                )

            team_mmrs[player_name] = player_stats[player_name].mmr
        return team_mmrs

    for game in games:
        # get team mmrs for rating groups
        ratingGroups = (__get_team_mmrs(game.team1), __get_team_mmrs(game.team2))
        ranks = [0, 1] if game.team1[0].win else [1, 0]

        # predict team1 win probability
        gamePrediction = __calculate_win_probability(ratingGroups)
        game_predictions.append(gamePrediction)

        # update trueskill based on match result
        updatedRatingGroups = trueskill.rate(ratingGroups, ranks)

        # keep track of mmr deltas
        playerMmrDeltas = {}

        # update player stats with new ratings
        for teamGroup in updatedRatingGroups:
            for playerName, updatedMMR in teamGroup.items():
                mmrDelta = updatedMMR.mu - player_stats[playerName].mmr.mu
                player_stats[playerName].mmr = updatedMMR
                playerMmrDeltas[playerName] = mmrDelta

        # handle in game stat updating
        for playerGameStats in game.players:
            playerName = playerGameStats.playerName

            # guaranteed playerName is in stats in mmr loop
            player_stats[playerName].add_game(
                game, playerGameStats, playerMmrDeltas[playerName]
            )

    return player_stats, game_predictions


def load_games(db: Database) -> list[Game]:
    """
    Loads game data from database and parses them into Game objects
    """
    matches_table = db["matches"]

    # get all games, sort asc
    query_results = matches_table.find().sort({"gameId": 1})

    games = []
    for i, match_data in enumerate(query_results):
        games.append(Game(i + 1, match_data))

    return games


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)

    db = get_database_connection(config["DB_CONNECTION_STRING"])
    games = load_games(db)

    playerStats, predictions = track_player_stats(games)

    for playerName, stats in sorted(playerStats.items(), key=lambda x: -x[1].mmr.mu):
        print(stats)
