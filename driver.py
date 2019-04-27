import discord, os, asyncio, signal, sys
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
    'blacklist [add/del/get] <[String] civilization name>': 'Adds to, deletes from, or gets the civilization blacklist.',
    'choose <[Int] player count> <(optional)[Int] civilization count>': 'Gets a random set of civilizations from n number of players. Players field is mandatory, civilizations field is optional.',
    'dlcs [enable/all/disable/none/get]': 'Enables, enables all, disables, disables all, or gets a list of all dlcs available for Civilization V.'
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

async def blacklist(message):
    global client
    global randomizer
    global confirm_emoji

    substrings = message.content.split(' ')
    if(len(substrings) == 3 and substrings[1].lower() == 'add'):
        randomizer.add_to_blacklist(substrings[2])
        await message.add_reaction(confirm_emoji)
    elif(len(substrings) == 3 and substrings[1].lower() == 'del'):
        randomizer.remove_from_blacklist(substrings[2])
        await message.add_reaction(confirm_emoji)
    elif((len(substrings) == 1) or (len(substrings) == 2 and substrings[1].lower() == 'get')):
        list = randomizer.get_blacklist()
        response = discord.Embed(title='Civilization Randomizer Blacklist', url=website, description='List of civs that will be explicitly removed from the pool.', color=0x58ff00)
        response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
        response.set_thumbnail(url=logo_url)
        for civ in list:
            response.add_field(name=civ, value='true', inline=True)
        await message.add_reaction(confirm_emoji)
        await message.channel.send(content=None, embed=response)
    else:
        await bad_command(message)

    if(utils.DELETE_AFTER_PROCESS): await message.delete()

async def dlcs(message):
    global client
    global randomizer
    global confirm_emoji

    substrings = message.content.split(' ')
    if(len(substrings) == 3 and substrings[1].lower() == 'enable'):
        randomizer.toggle_dlc(substrings[2], True)
        await message.add_reaction(confirm_emoji)
    elif(len(substrings) == 2 and substrings[1].lower() == 'all'):
        randomizer.toggle_all_dlcs(True)
        await message.add_reaction(confirm_emoji)
    elif(len(substrings) == 3 and substrings[1].lower() == 'disable'):
        randomizer.toggle_dlc(substrings[2], False)
        await message.add_reaction(confirm_emoji)
    elif(len(substrings) == 2 and substrings[1].lower() == 'none'):
        randomizer.toggle_all_dlcs(False)
        await message.add_reaction(confirm_emoji)
    elif((len(substrings) == 1) or (len(substrings) == 2 and substrings[1].lower() == 'get')):
        list = randomizer.get_dlcs()
        response = discord.Embed(title='Civilization Randomizer DLCs List', url=website, description='List of all DLCs available for Civilization V.', color=0x58ff00)
        response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
        response.set_thumbnail(url=logo_url)
        for dlc_name,hash in list.items():
            response.add_field(name=dlc_name, value=str('Enabled: ' + str(hash['enabled'])), inline=False)
        await message.add_reaction(confirm_emoji)
        await message.channel.send(content=None, embed=response)
    else:
        await bad_command(message)

    if(utils.DELETE_AFTER_PROCESS): await message.delete()

async def bad_command(message):
    global client

    utils.log(1, 'Cannot process this command: ' + message.content + '\n\tIgnoring!')
    if(utils.DELETE_AFTER_PROCESS): await message.delete()
    await message.channel.send(content=('**<@' + str(message.author.id) + '> Bad command: \"' + message.content + '\"!** *(Try using ' + message_prefix(message.content) + "help for correct usage)*"))

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

        if(command == 'blacklist'):
            await set_status(bot_status('Makin a list...'), discord.Status.dnd)
            await blacklist(message)
        elif(command == 'choose'):
            await set_status(bot_status('Rolling dice...'), discord.Status.dnd)
            await choose(message)
        elif(command == 'dlcs'):
            await set_status(bot_status('Checking it twice...'), discord.Status.dnd)
            await dlcs(message)
        elif(command == "help"):
            await set_status(bot_status('Getting help...'), discord.Status.dnd)
            await usage(message)
        else:
            await set_status(bot_status('Invalid command!'), discord.Status.dnd)
            await bad_command(message)

        await set_status(bot_status(), discord.Status.online)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
