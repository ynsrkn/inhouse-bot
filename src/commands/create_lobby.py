from discord import Embed


def create_lobby(discord_author: str) -> Embed:
    # TODO add admin functionality (currently only yunis1 is an admin)
    if discord_author != "yunis1":
        return Embed(title="Only admins can use this command")
