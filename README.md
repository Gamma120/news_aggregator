# News Aggregator

The goal is to **feed a discord channel/server of news from a cutomisable list of sites that provide [RSS flux](https://en.wikipedia.org/wiki/RSS).** 

## Usage

**Step 1:** create a [discord bot](https://discordpy.readthedocs.io/en/stable/discord.html) and add it to your discord server

**Step 2:** add your bot token to [discord bot](./src/discord_bot.py)
```python
client.run('your token')
```

**Step 3:** install dependencies (maybe in a [virtual environnement](https://docs.python.org/3/library/venv.html))
```bash
pip install -r path/to/project_directory/requierment.txt
```

**Step 4:** run 
```bash 
cd path/to/project_directory/
python main.py
```

Your bot should be now connected in discord.

**Step 5:**
- `$help` to see the commandes. 
- `$add_rss <flux_name> <url>` to add your first RSS flux

**Step 5 (alternative in futur release):** populate [RSS sources](./rss_sources.txt) with links to xml sources and names for the flux

```
# Add URLs of files from sites you want to fetch
# Split URL and file name by ;
# Uncomment the line below to test
# Fin du Game;https://fin-du-game.lepodcast.fr/rss
```

`$add_rss <file_name>` to add RSS flux in the file

**Step 6:** `$update`

## Why does this project exist?
The motivation was to have a single place to gather everything I want to be up-to-date, on a tool that I use daily. It was first intended to track news but it can take advantage of any site that provide RSS flux, from new episodes on CrunchyRoll to the latest package of your favorite python library.
And last, because why not. Fun project to familiarise with python, git and everything in-between.