from unicodedata import east_asian_width


class PlayerName:

    def __init__(self, summonerName: str, name: str, tag: str) -> None:
        # check if name has any east asian width characters
        # if so use summonerName instead and hope it doesnt
        has_fullwidth = False
        for c in name:
            if east_asian_width(c) in ["W", "F", "A"]:
                has_fullwidth = True
                break
        if has_fullwidth:
            self.name = summonerName.lower()
            self.displayName = summonerName
        else:
            self.name = name.lower()
            self.displayName = name

        self.summonerName: str = summonerName
        self.tag: str = tag

    def __eq__(self, other):
        return self.name == other.name and self.tag == other.tag
