import discord
import os
import asyncio
import signal
import sys
import choose as c
import utilities as utils

#
# Stuff to use in runtime
#
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

class ImposibleReactionResolve(Exception):
    def __init__(self):
        utils.log(3, "Reaction confirmation could not resolve!")

def bot_status(message=DEFAULT_BOT_STATUS):
    global prefix
    return (prefix + "help" + " | " + message)

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

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        utils.log(1, 'TIMEOUT EVENT!')
        await self._callback()

    def cancel(self):
        self._task.cancel()

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
        global confirm_emoji
        global deny_emoji
        if(utils.DEBUG): utils.log(2, 'Confirm: ' + str(str(reaction) == confirm_emoji) + '\t\tDeny: ' + str(str(reaction) == deny_emoji))
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

    if(utils.DEBUG):
        utils.log(2, '' + str(message.channel) + '\t' + str(message.mention_everyone))

    await message.channel.send(content=None, embed=help_message)

async def choose(message):
    global client
    global randomizer

    argv = message.content.split(' ')
    argc  = len(argv)
    results = {}

    if(argc == 2): results = randomizer.choose(int(argv[1]))
    elif(argc == 3): results = randomizer.choose(int(argv[1]), civilization_count=int(argv[2]))

    response = discord.Embed(title='Civilization Randomizer Results', url=website, description='Results of the randomizer.', color=0x58ff00)
    response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
    response.set_thumbnail(url=logo_url)

    utils.log(0, 'Player Civilization selections:')
    for player,civilizations in results.items():
        civilization_string = "Choose from: "
        for i in civilizations:
            if(i != civilizations[-1]): civilization_string += i + ', '
            else: civilization_string += 'or ' + i
        response.add_field(name=player, value=civilization_string, inline=False)

    if(utils.DELETE_AFTER_PROCESS): await message.delete()
    await message.channel.send(content=None, embed=response)

async def bad_command(message):
    global client

    utils.log(1, 'Cannot process this command: ' + message.content + '\n\tIgnoring!')
    if(utils.DELETE_AFTER_PROCESS): await message.delete()
    await message.channel.send(content=('**<@' + str(message.author.id) + '> Bad command: \"' + message_prefix(message.content) + message_suffix(message.content) + '\"!** *(Try using ' + message_prefix(message.content) + "help for correct usage)*"))

#
# Initialization
#
client = discord.Client()
randomizer = c.CivRandomizer()
bot_token = os.getenv('CIV_BOT_TOKEN')

#
# Discord event stuff
#
@client.event
async def on_ready():
    utils.log(0, 'Client logged in as the user ' + str(client.user) + '\n\tID: ' + str(client.user.id) + '\n\tBOT: ' + str(client.user.bot) + '\n\tDisplay Name: ' + str(client.user.display_name))
    await set_status(bot_status(DEFAULT_BOT_STATUS), discord.Status.online)

@client.event
async def on_message(message):
    # Check if message has correct prefix
    if(is_command(message.content)):
        # Console confirmation that a relevant command was received
        utils.log(0, 'Timestamp(' + str(message.created_at) + ') UserID(' + str(message.author) + ') Message(' + message.content + ')')

        # Get the action map of the command suffix
        command = message_suffix(message.content)

        if(command == "help"):
            await set_status(bot_status('Getting help...'), discord.Status.dnd)
            await usage(message)
        elif(command == 'choose'):
            await set_status(bot_status('Rolling dice...'), discord.Status.dnd)
            await choose(message)
        else:
            await set_status(bot_status('Invalid command!'), discord.Status.dnd)
            await bad_command(message)

        await set_status(bot_status(), discord.Status.online)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
