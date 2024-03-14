# inhouse-bot


A Discord bot built with `py-cord` to show stats for League of Legends Custom Games.

## Usage

- Open the `League of Legends` client.

- Download the [LCU Explorer](https://github.com/HextechDocs/lcu-explorer) and try out a local API endpoint to find the `port` and `Basic Auth Key` that your client is currently using.

- Run `python3 scrape_match_data.py <port> <authkey>` to pull match data from your client.

- Edit the `GUILD_IDS` constant at the top of the `inhouse_bot.py` and add your own guild ids.

- Run `python3 inhouse_bot.py` to start the Discord bot.