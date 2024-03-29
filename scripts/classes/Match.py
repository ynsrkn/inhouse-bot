from generate_player_stats import Game

class Match:
    def __init__(self, game: Game, prediction: float) -> None:
        self.game = game
        self.prediction = prediction
