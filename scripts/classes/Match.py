from generate_player_stats import Game

class Match:
    def __init__(self, game: Game, prediction: float) -> None:
        self.game: Game = game
        self.prediction: float = prediction
