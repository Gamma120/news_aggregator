import os
from discord.ext import commands
from ast import literal_eval

from src.utils import *
from src.rss_bot import RSS_Bot
from src.database import Database

bot = commands.Bot(command_prefix='$', help_command=None)
db_path = os.path.join(PRJCT_DB,'news_aggregator.db')
db = Database(db_path)
rss_bot = RSS_Bot()
    
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(name='show_rss',
             description='Show all subscribed rss flux of the channel',
             usage='',
             help='')
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



@bot.command(name='show_all',
             description='Show rss flux from all channels.',
             usage='',
             help='')
async def show_all(ctx):
    # Get list
    rss_list = db.get_rss_flux_list()
    
    # Construct the message
    if len(rss_list) == 0:
        message="No active RSS flux. Add one with `$add_rss` command."
    else:
        message="Currently active RSS flux:\n```"
        for rss_flux in rss_list:
            message+=f"{rss_flux}\n"
        message+="```For more information on a RSS flux, type `$info <flux_name>`."
    await ctx.send(message)



@bot.command(name='info',
             description='Display all information on a rss flux',
             usage='<flux name>',
             help='')
async def info(ctx, flux_name: str):
    channel = ctx.channel
    row = db.get_rss_row({'name': flux_name,'channel': channel.id})
    
    message=f'Informations found about {flux_name}:\n```'
    for key in row.keys():
        message+=f'{key}: {row[key]}\n'
    message+='```To edit this flux, type `$edit_rss '+flux_name+' {<key>:<value>,...}`.'
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
             usage='<flux_name>',
             help='')
async def remove_rss(ctx, flux_name: str):
    channel = ctx.channel
    channel_id = channel.id
    db.remove_rss_flux(flux_name,channel_id)
    await ctx.send(f"{flux_name} remove from {channel.name}.")



@bot.command(name='edit_rss',
             description='Edit a rss flux.',
             usage='<flux name> {<key>:<value>,...}',
             help='Update rate format : XdXhXm')
async def edit_rss(ctx, flux_name: str, edit_dict: str = None):
    channel = ctx.channel
    edit_dict = literal_eval(edit_dict)
    # TODO : handle errors
    db.edit_rss_flux(flux_name, channel.id, edit_dict)
    await ctx.send(f'{flux_name} edited.')



@bot.command(name='update',
             description='Fetch rss flux and post new items.',
             usage='',
             help='')
async def update(ctx):
    to_fetch_list = db.to_fetch()
    fetched_list = rss_bot.fetch(to_fetch_list, PRJCT_RSS)
    now = date_to_int(datetime.utcnow())
    for rss in fetched_list:
        xml_path = os.path.join(PRJCT_RSS,rss['file_name'])
        stop_title = rss['last_item']
        channel = bot.get_channel(int(rss['channel']))
        rss_bot.xml_strip(xml_path, stop_title)
        db.edit_rss_flux(rss['name'], rss['channel'],{'last_time_fetched': now})
        items_list = rss_bot.get_items(xml_path)
        os.remove(xml_path)
        for item in items_list:
            message=''
            for key in item.keys():
                message+=f'{key}: {item[key]}\n'
            await channel.send(message)
        if(len(items_list) != 0) :
            last_item = items_list[0]['title']
            db.edit_rss_flux(rss['name'],rss['channel'],{'last_item': last_item})
    await ctx.send("Update completed.")
    


@bot.command(name='import',
             description='Add rss flux from file in attachement.',
             usage='<file_to_import>',
             help='Format of the file:\n'
             'flux name;url[;channel[;last item[;last time fetched[;update rate]]]]\n'
             'If the channel is not provided, it will be the one the command was invoke in.\n'
             'Update rate format : XdXhXm')
async def _import(ctx):
    logger = get_logger()
    channel = ctx.channel
    author_name = ctx.author.name
    author_id = ctx.author.id
    
    attachments = ctx.message.attachments
    if(len(attachments)!=1):
        await ctx.send("Please provide a file in attachement.")
        await help(ctx,"import")
    else:
        file = attachments[0]
        if(file.content_type != "text/plain; charset=utf-8"):
            await ctx.send("Please provide a text file.\nProvided "+file.content_type)
        else:
            file_name = file.filename
            file_path = os.path.join(PRJCT_TMP,file_name)
            logger.info(author_name +" (" + str(author_id) + ") imported " + file_name)
            await file.save(file_path)
            db.import_list(file_path,channel.id)
            await ctx.send("Import successful")



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
             usage='<arguments...>',
             help='')
async def echo(ctx,*args):
    arguments = ' '.join(args)
    await ctx.send(arguments)
    
      
def run():
    bot.run('')