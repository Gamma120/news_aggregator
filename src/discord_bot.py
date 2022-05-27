from discord.ext import commands
from os import path

from utils import *
from database import Database

bot = commands.Bot(command_prefix='$', help_command=None)
db_path = path.join(PRJCT_DB,'news_aggregator.db')
db = Database(db_path)
    
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(name='show_rss',
             description='Show all subscribed rss flux of the channel')
async def show_rss(ctx):
    # Get list
    channel = ctx.channel
    rss_list = db.get_rss_flux_list(channel.id)
    
    # Construct the message
    if len(rss_list) == 0:
        message="No active RSS flux in this channel. Add one with `$add_rss` command."
    else:
        message="Currently active RSS flux in this channel:\n```"
        for rss_flux in rss_list:
            message+=f"{rss_flux}\n"
        message+="```For more information on a RSS flux, type `$info <flux_name>`."
    await ctx.send(message)


@bot.command(name='add_rss',
             description='Add rss flux from argument',
             usage='<flux_name> <url> [<channel>] [<update rate>]',
             help='If the channel is not provided, it will be the one the command was invoke in.\n'
             'Update rate format : XdXhXm')
async def add_rss(ctx, flux_name: str, url: str, *args : str):
    channel = ctx.channel
    # TODO : handle the others args
    channel_id = channel.id
    rss_flux = {'name': flux_name, 'url':url}
    # dattabase should raise errors and be handled here
    db.add_rss_flux(rss_flux, channel_id)
    await ctx.send(f"{flux_name} added to {channel.name}.")

@bot.command(name='remove_rss',
             description='Remove rss flux form argument',
             usage='<flux_name>')
async def remove_rss(ctx, flux_name: str):
    channel = ctx.channel
    channel_id = channel.id
    db.remove_rss_flux(flux_name,channel_id)
    await ctx.send(f"{flux_name} remove from {channel.name}.")

@bot.command(name='import',
             description='Add rss flux from file in argument.',
             usage='<file_to_import>',
             help='Format of the file:\n'
             'flux name;url[;channel[;last item[;last time fetched[;update rate]]]]\n'
             'If the channel is not provided, it will be the one the command was invoke in.\n'
             'Update rate format : XdXhXm')
async def _import(ctx, arg: str):
    channel = ctx.channel
    
    await ctx.send("Import completed.")

@bot.command(name='help',
             description='Return description on the command in argument.',
             usage='<command>',
             help='If no command provided in argument, display all commands available.')
async def help(ctx, arg: str = None):
    if arg==None:
        helptext='Available commands:\n```'
        for command in bot.commands:
            helptext+=f"{command}\t{command.description}\n"
        helptext+='Type $help <command> for more info on a command.```'
        await ctx.send(helptext)
    else:
        found=False
        for cmd in bot.commands:
            if arg==cmd.name:
                helptext=f'**{cmd.name}**:\n```{cmd.description}\nUsage: ${cmd.name} {cmd.usage}\n{cmd.help}```'
                await ctx.send(helptext)
                found=True

        if not found:
            helptext='Available commands:\n```'
            for command in bot.commands:
                helptext+=f"{command}\t{command.description}\n"
            helptext+='Type $help <command> for more info on a command.```'
            await ctx.send(helptext)

@bot.command(name='echo',
             description='Return arguments',
             usage='<arguments...>')
async def echo(ctx,*args):
    arguments = ' '.join(args)
    await ctx.send(arguments)
    
      
if __name__ == "__main__":
    set_directories()
    bot.run('')