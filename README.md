# News Aggregator

The goal is to **feed a discord channel/server of news from a cutomisable list of sites that provide [RSS flux](https://en.wikipedia.org/wiki/RSS).** 

## Usage

**Step 1:** populate [RSS sources](./rss_sources.txt) with links to xml sources and names for the files

```
# Add URLs of files from sites you want to fetch
# Split URL and file name by ;
# Uncomment the line below to test
# https://fin-du-game.lepodcast.fr/rss;fin-du-game.xml
```
**Step 2:** create a [discord bot](https://discordpy.readthedocs.io/en/stable/discord.html)

**Step 3:** add your bot token to [discord bot](./src/discord_bot.py)
```python
client.run('your token')
```

**Step 4:** install dependencies
```bash
pip install -r path/to/project_directory/requierment.txt
```

**Step 5:** run 
```bash 
python path/to/project_directory/src/rss_bot.py
python path/to/project_directory/src/discord_bot.py
```

**Step 4:** currently just downloading the xml, discord bot responding to `$hello`

## TODO

- [ ] make it a service
- [ ] fork the fetch of xmls
- [ ] cron
- [ ] add sql database
- [x] continuous integration
- [ ] make package
- [ ] discord commands

## Future Features

- customize the update time of each source
- add keywords, used as filters to only post what relevant for you
- commands in discord to configure the bot (add new RSS flux, filters...)

## Why does this project exist?
The motivation was to have a single place to gather everything I want to be up-to-date, on a tool that I use daily. It was first intended to track news but it can take advantage of any site that provide RSS flux, from new episodes on CrunchyRoll to the latest package of your favorite python library.
And last, because why not. Fun project to familiarise with python, git and everything in-between.