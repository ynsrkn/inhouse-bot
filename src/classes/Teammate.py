from src.classes.PlayerName import PlayerName


class Teammate:
    def __init__(self, name: PlayerName) -> None:
        self.name = name
        self.wins = 0
        self.losses = 0
        self.gamesPlayed = 0
        self.winrate = 0

    def add_game(self, win: bool) -> None:
        if win:
            self.wins += 1
        else:
            self.losses += 1
        self.gamesPlayed += 1
        self.winrate = int(round(self.wins / self.gamesPlayed * 100))

    def __repr__(self) -> str:
        return f"{self.wins}W {self.losses}L ({self.winrate})"
