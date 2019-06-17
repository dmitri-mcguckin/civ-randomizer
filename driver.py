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
    'ban <[String/Array]>': 'Bans civ(s)',
    'unban <[String/Array]>': 'Unbans civ(s)',
    'blacklist [empty] <[String] civilization name>': '`<Nothing>` gets the blacklist, `empty` empties it.',
    'choose <[Int] player_count> <(optional)[Int] civilization_count>': '`<Nothing>` gets a list of civilizations that can be randomly selected, otherwise gets `player_count` number of random selections of size `civilization_count`.',
    'dlcs [enable/all/disable/none/get] <[String] dlc_name>': '`<Nothing>` gets a list of all available dlcs, `enable` enables `dlc_name`, `all` enables all dlcs, `disable` disables `dlc_name`, `none` disables all dlcs'
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

async def set_status(status_message, new_status):
    global client
    game = discord.Game(status_message)
    await client.change_presence(status=new_status, activity=game)

async def usage(message):
    global client
    global confirm_emoji

    help_message = discord.Embed(title='Civilization Randomizer Help', url=website, description='Command info and details.', color=0xef2715)
    help_message.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
    help_message.set_thumbnail(url=logo_url)

    for command in commands.keys():
        help_message.add_field(name=str(prefix + command), value=str(commands[command]), inline=False)

    if(utils.DEBUG):
        utils.log(2, '' + str(message.channel) + '\t' + str(message.mention_everyone))

    await message.add_reaction(confirm_emoji)
    await message.channel.send(content=None, embed=help_message)

async def choose(message):
    global client
    global randomizer

    argv = message.content.split(' ')
    argc  = len(argv)
    results = {}

    if(argc > 1):
        if(argc == 2): results = randomizer.choose(int(argv[1]))
        elif(argc == 3): results = randomizer.choose(int(argv[1]), civilization_count=int(argv[2]))

        response = discord.Embed(title='Civilization Randomizer Results', url=website, description='Results of the randomizer.', color=0xf4fc07)
        response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
        response.set_thumbnail(url=logo_url)

        if(len(results) == 0):
            utils.log(2, 'Got an empty list back from the randomizer! No choose!')
            await message.add_reaction(deny_emoji)
            return
        else:
            await message.add_reaction(confirm_emoji)
            utils.log(0, 'Player Civilization selections:')
            for player,civilizations in results.items():
                civilization_string = "Choose from: "
                for i in civilizations:
                    if(i != civilizations[-1]): civilization_string += i + ', '
                    else: civilization_string += 'or ' + i
                response.add_field(name=player, value=civilization_string, inline=False)

            await message.channel.send(content=None, embed=response)
    else:
        size = len(randomizer.get_choose_pool())
        if(size >= 20):
            response_1 = discord.Embed(title='Civilization Randomizer Choose Pool', url=website, description='List of civs to chose from.', color=0x07fc28)
            response_1.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
            response_1.set_thumbnail(url=logo_url)

            response_2 = discord.Embed(title='Civilization Randomizer Choose Pool Cont.', url=website, description='Continued list of civs to chose from.', color=0x07fc28)
            response_2.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
            response_2.set_thumbnail(url=logo_url)

            half = size // 2
            list_1 = randomizer.get_choose_pool()[:half]
            list_2 = randomizer.get_choose_pool()[half:]

            for civ in list_1:
                response_1.add_field(name=civ, value='true', inline=True)
            for civ in list_2:
                response_2.add_field(name=civ, value='true', inline=True)

            await message.add_reaction(confirm_emoji)
            await message.channel.send(content=None, embed=response_1)
            await message.channel.send(content=None, embed=response_2)
        else:
            response = discord.Embed(title='Civilization Randomizer Choose Pool', url=website, description='List of civs that be chosen from.', color=0x07fc28)
            response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
            response.set_thumbnail(url=logo_url)
            for civ in randomizer.get_choose_pool():
                response.add_field(name=civ, value='true', inline=True)
            await message.add_reaction(confirm_emoji)
            await message.channel.send(content=None, embed=response)

    if(utils.DELETE_AFTER_PROCESS): await message.delete()

async def ban(message):
    substrings = message.content.split(' ')
    if(len(substrings) >= 2):
        for i in range(1, len(substrings)):
            if(utils.DEBUG): utils.log(0, 'Adding value: #' + str(i) + ' ' + substrings[i] + ' of ' + str(len(substrings) - 2) + ' entries.')
            randomizer.add_to_blacklist(substrings[i])
        randomizer.reform_pool()
        await message.add_reaction(confirm_emoji)
    else:
        await message.add_reaction(deny_emoji)
        await bad_command(message)

async def unban(message):
    substrings = message.content.split(' ')
    if(len(substrings) >= 2):
        for i in range(1, len(substrings)):
            if(utils.DEBUG): utils.log(0, 'Removing value: #' + str(i) + ' ' + substrings[i] + ' of ' + str(len(substrings) - 2) + ' entries.')
            randomizer.remove_from_blacklist(substrings[i])
        randomizer.reform_pool()
        await message.add_reaction(confirm_emoji)
    else:
        await message.add_reaction(deny_emoji)
        await bad_command(message)

async def blacklist(message):
    global client
    global randomizer
    global confirm_emoji
    global deny_emoji

    substrings = message.content.split(' ')
    if(len(substrings) == 2 and substrings[1].lower() == 'empty'):
        randomizer.empty_blacklist()
        randomizer.reform_pool()
        await message.add_reaction(confirm_emoji)
    elif(len(substrings) == 1):
        list = randomizer.get_blacklist()
        response = discord.Embed(title='Civilization Randomizer Blacklist', url=website, description='List of civs that will be explicitly removed from the pool.', color=0x2407fc)
        response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
        response.set_thumbnail(url=logo_url)
        for civ in list:
            response.add_field(name=civ, value='true', inline=True)
        await message.add_reaction(confirm_emoji)
        await message.channel.send(content=None, embed=response)
    else:
        await message.add_reaction(deny_emoji)
        await bad_command(message)

    if(utils.DELETE_AFTER_PROCESS): await message.delete()

async def dlcs(message):
    global client
    global randomizer
    global confirm_emoji
    global deny_emoji

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
    elif(len(substrings) == 1):
        list = randomizer.get_dlcs()
        response = discord.Embed(title='Civilization Randomizer DLCs List', url=website, description='List of all DLCs available for Civilization V.', color=0xa207fc)
        response.set_author(name='Civilization Randomizer', url=website, icon_url=logo_url)
        response.set_thumbnail(url=logo_url)
        for dlc_name,hash in list.items():
            response.add_field(name=dlc_name, value=str('Enabled: ' + str(hash['enabled'])), inline=False)
        await message.add_reaction(confirm_emoji)
        await message.channel.send(content=None, embed=response)
    else:
        await message.add_reaction(deny_emoji)
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
        elif(command == 'ban'):
            await set_status(bot_status('Banning...'), discord.Status.dnd)
            await ban(message)
        elif(command == 'unban'):
            await set_status(bot_status('Unbanning...'), discord.Status.dnd)
            await unban(message)
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
            await message.add_reaction(deny_emoji)
            await bad_command(message)

        await set_status(bot_status(), discord.Status.online)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
