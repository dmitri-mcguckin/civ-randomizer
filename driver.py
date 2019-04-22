import discord
import os
import signal
import sys
import choose as c
import utilities as utils

def update_default_bot_status():
    global active_bot_status
    active_bot_status = prefix + "help" + " | " + bot_status

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

    help_message = discord.Embed(title='Civ Randomizer Help', url=website, description='Command info and details.', color=0x58ff00)
    help_message.set_author(name='Word Bot', url=website, icon_url=logo_url)
    help_message.set_thumbnail(url=logo_url)

    for command in commands.keys():
        help_message.add_field(name=str(prefix + command), value=str(commands[command]), inline=False)

    if(debug):
        utils.log(2, '' + str(message.channel) + '\t' + str(message.mention_everyone))

    await message.delete()
    await message.channel.send(content=None, embed=help_message)

async def choose(message):
    global client

    argv = message.content.split(' ')
    argc  = len(argv)
    if(argc == 2): player_civs = c.pChoose(int(argv[1]))
    elif(argc == 3): player_civs = c.pChoosec(int(argv[1]), int(argv[2]))

    response = discord.Embed(title='Civilization Randomizer Results', url=website, description='Results of the randomizer.', color=0x58ff00)
    response.set_author(name='Civ Randomizer', url=website, icon_url=logo_url)
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
commands = {
    'help': 'Stop it, get some help.',
    'choose <[Int] players> <[Int] civilizations>': 'Gets a random set of civilizations from n number of players. Players field is mandatory, civilizations field is optional.'
}
bot_status = ''
active_bot_status = 'Twiddling thumbs...'
website = 'https://github.com/mackkcooper/CivVSelect'
logo_url = 'https://i.imgur.com/pBgN2gZ.jpg'
update_default_bot_status()

#
# Discord event stuff
#

@client.event
async def on_ready():
    utils.log(0, 'Client logged in as the user ' + str(client.user) + '\n\tID: ' + str(client.user.id) + '\n\tBOT: ' + str(client.user.bot) + '\n\tDisplay Name: ' + str(client.user.display_name))
    await set_status(active_bot_status, discord.Status.idle)

@client.event
async def on_message(message):
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

        bot_status = active_bot_status
        await set_status(bot_status, discord.Status.idle)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
