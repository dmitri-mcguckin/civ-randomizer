import discord
import os
import asyncio
import signal
import sys
import choose as c
import utilities as utils

class ImposibleReactionResolve(Exception):
    def __init__(self):
        utils.log(3, "Reaction confirmation could not resolve!")

def bot_status():
    global DEFAULT_BOT_STATUS
    global prefix
    return (prefix + "help" + " | " + DEFAULT_BOT_STATUS)

async def handle_forced_exit():
    global client

    print('\n')
    utils.log(0, 'A signal was received to shutdown the bot!')
    await client.logout()
    sys.exit(0)

def message_prefix(message):
    return message[0:len(prefix)]

def message_suffix(message):
    return message[len(prefix):].split(' ')[0]

def message_argument(message):
    return message[len(prefix):].split(' ')[1]

def is_command(message):
    return (message_prefix(message) == prefix)

async def set_status(status_message, new_status):
    global client
    game = discord.Game(status_message)
    await client.change_presence(status=new_status, activity=game)

async def resolve_confirmation(message, question):
    global client
    global response_timeout
    global confirm_emoji
    global deny_emoji

    def reactor_is_author(reaction, user):
        global debug
        global confirm_emoji
        global deny_emoji
        if(debug): utils.log(2, 'Confirm: ' + str(str(reaction) == confirm_emoji) + '\t\tDeny: ' + str(str(reaction) == deny_emoji))
        return (user == message.author and ((str(reaction.emoji) == confirm_emoji) or (str(reaction.emoji) == deny_emoji)))

    response = await message.channel.send(content=question)
    can_resolve = False;
    await response.add_reaction(confirm_emoji)
    await response.add_reaction(deny_emoji)

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=response_timeout, check=reactor_is_author)

        if(str(reaction) == confirm_emoji):
            can_resolve = True
        elif(str(reaction) == deny_emoji):
            can_resolve = False
        else:
            raise ImposibleReactionResolve()
    except asyncio.TimeoutError:
        raise ImposibleReactionResolve()

    await response.delete()
    return can_resolve

async def usage(message):
    global client

    help_message = discord.Embed(title='Civilization Randomizer Help', url=website, description='Command info and details.', color=0x58ff00)
    help_message.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
    help_message.set_thumbnail(url=logo_url)

    for command in commands.keys():
        help_message.add_field(name=str(prefix + command), value=str(commands[command]), inline=False)

    if(debug):
        utils.log(2, '' + str(message.channel) + '\t' + str(message.mention_everyone))

    await message.channel.send(content=None, embed=help_message)

async def choose(message):
    global client

    argv = message.content.split(' ')
    argc  = len(argv)
    player_civs = {}

    try:
        if(argc == 2): player_civs = c.pChoose(int(argv[1]))
        elif(argc == 3): player_civs = c.pChoosec(int(argv[1]), int(argv[2]))
    except c.GreedyPlayer:
        try:
            result = await resolve_confirmation(message, 'No civilization pool size was specified, but recommended size is: ' + str(c.recommended_pool_size(argv[1])) + '. Would you like to use this setting?')

            if(result):
                c.reset_pool()
                utils.log(2, 'Players: ' + argv[1] + '\tCivilizations: ' + str(c.recommended_pool_size(argv[1])))
                player_civs = c.pChoose(int(argv[1]))
            else:
                await message.channel.send(content='**Canceling dice roll!**')
                message.delete()
                return
        except ImposibleReactionResolve as e:
            utils.log(3, 'Could not resolve reaction: ' + str(e) + '\n\tThrowing out thread!')
            await message.channel.send(content='**Canceling dice roll!**')
            await message.delete()
            return

    response = discord.Embed(title='Civilization Randomizer Results', url=website, description='Results of the randomizer.', color=0x58ff00)
    response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
    response.set_thumbnail(url=logo_url)

    utils.log(0, 'Player Civilization selections:')
    for player in range(0,len(player_civs)):
        utils.log(0, '\tPlayer ' + str(player) + ': ' + str(player_civs[player]))
        response.add_field(name=str('Player ' + str(player + 1) + ':'), value=str('Choose from: ' + str(player_civs[player])), inline=False)

    await message.delete()
    await message.channel.send(content=None, embed=response)

async def bad_command(message):
    global client

    utils.log(1, 'Cannot process this command: ' + message.content + '\n\tIgnoring!')
    await message.delete()
    await message.channel.send(content=('**<@' + str(message.author.id) + '> Bad command: \"' + message_prefix(message.content) + message_suffix(message.content) + '\"!** *(Try using ' + message_prefix(message.content) + "help for correct usage)*"))

#
# Initialization
#
client = discord.Client()
bot_token = os.getenv('CIV_BOT_TOKEN')

#
# Stuff to use in runtime
#
debug = True
prefix = 'c!'
response_timeout = 5
confirm_emoji = "\u2705"
deny_emoji = "\u26d4"
commands = {
    'help': 'Stop it, get some help.',
    'choose <[Int] players> <[Int] civilizations>': 'Gets a random set of civilizations from n number of players. Players field is mandatory, civilizations field is optional.'
}
DEFAULT_BOT_STATUS = 'Twiddling thumbs...'
website = 'https://github.com/dmitri-mcguckin/civ-randomizer'
logo_url = 'https://i.imgur.com/pBgN2gZ.jpg'

#
# Discord event stuff
#
@client.event
async def on_ready():
    utils.log(0, 'Client logged in as the user ' + str(client.user) + '\n\tID: ' + str(client.user.id) + '\n\tBOT: ' + str(client.user.bot) + '\n\tDisplay Name: ' + str(client.user.display_name))
    await set_status(DEFAULT_BOT_STATUS, discord.Status.idle)

@client.event
async def on_message(message):
    c.reset_pool()
    # Check if message has correct prefix
    if(is_command(message.content)):
        # Console confirmation that a relevant command was received
        utils.log(0, 'Timestamp(' + str(message.created_at) + ') UserID(' + str(message.author) + ') Message(' + message.content + ')')

        # Get the action map of the command suffix
        command = message_suffix(message.content)

        if(command == "help"):
            await set_status('Getting help...', discord.Status.dnd)
            await usage(message)
        elif(command == 'choose'):
            await set_status('Rolling dice...', discord.Status.dnd)
            await choose(message)
        else:
            await set_status('Invalid command!', discord.Status.dnd)
            await bad_command(message)

        await set_status(bot_status(), discord.Status.online)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
