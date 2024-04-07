# inhouse-bot


A Discord bot built with `py-cord` to show stats for League of Legends Custom Games.

## Installation

- Clone the repository and add a `config.yaml` file in the project root with the following properties:

```
DB_CONNECTION_STRING: <STRING>
DISCORD_TOKEN: <TOKEN>
GUILD_IDS: [123, 456]
```

- Run `pip install -r requirements.txt` to install dependencies.

## Usage

- Open and login to the `League of Legends` client. It needs to be open to scrape local custom game match history data.

- From the `scripts` directory run `python inhouse_bot.py` to start the Discord bot.
