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

@bot.command(name='add_rss',
             description='Add rss flux from argument',
             usage='<flux_name> <url> [<channel>] [<update rate>]',
             help='If the channel is not provided, it will be the one the command was invoke in.\n'
             'Update rate format : XdXhXm')
async def add_rss(ctx, args):
    channel = ctx.channel

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