# inhouse-bot


A Discord bot built with `py-cord` to show stats for League of Legends Custom Games.

## Installation

- Clone the repository and add a `secrets.json` file with `token: <YOUR_TOKEN>` in the project root.

- Run `pip install -r requirements.txt` to install dependencies.

- Edit the `GUILD_IDS` constant at the top of `scripts/inhouse_bot.py` and add your own guild ids.

## Usage

- Open and login to the `League of Legends` client. It needs to be open to scrape local custom game match history data.

- From the `scripts` directory run `python3 inhouse_bot.py` to start the Discord bot.
