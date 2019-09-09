import discord, os, asyncio, choose, time
import utilities as utils

#
# Stuff to use in runtime
#
bot_status = {
    'online': discord.Status.online,
    'offline': discord.Status.offline,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
}

commands = utils.load_json(os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/commands.json")
prefix = 'c!'
response_timeout = 5
confirm_emoji = "\u2705"
deny_emoji = "\u26d4"

DEFAULT_BOT_STATUS = 'Twiddling thumbs...'
DEFAULT_WEBSITE = 'https://web.cecs.pdx.edu/~dmitri3'
DEFAULT_LOGO = 'https://i.imgur.com/pBgN2gZ.jpg'

#
# Discordy things
#
def create_embed(title, description, author=None, color=0x7625d9):
    if(author == None): author = client.user.name
    embed = discord.Embed(title=title, description=description, url=DEFAULT_WEBSITE, color=color)
    embed.set_author(name=author, url=DEFAULT_WEBSITE, icon_url=DEFAULT_LOGO)
    embed.set_thumbnail(url=DEFAULT_LOGO)

    return embed

async def usage(message):
    await confirm_message(message)
    usage_msg = create_embed('Civilization Randomizer Bot', 'General usage and commands.')

    for command, data in commands.items():
        if(data[0] != ""): usage_msg.add_field(name=prefix + command + " [" + data[0] + "]", value=data[1], inline=False)
        else: usage_msg.add_field(name=prefix + command, value=data[1], inline=False)

    await message.channel.send(embed=usage_msg)

async def set_default_status(): await set_status(prefix + 'help | ' + DEFAULT_BOT_STATUS, status='idle')

async def set_status(status_message, status='online'):
    activity = discord.Game(status_message)
    await client.change_presence(status=bot_status[status], activity=activity)

async def confirm_message(message): await message.add_reaction(confirm_emoji)
async def deny_message(message): await message.add_reaction(deny_emoji)

#
# Civ bot things
#
async def choose_civs(message, args):
    player_results = []

    if(len(args) == 1 or len(args) == 2):
        utils.log(0, "Got argument(s) for choose: " + str(args))

        try:
            for arg in args: int(arg)
        except ValueError as e:
            await deny_message(message)
            utils.log(3, str(e) + "\n\tGracefully skipping processing this command.")
            return

        await confirm_message(message)

        if(len(args) == 1): player_results = randomizer.choose(int(args[0]))
        elif(len(args) == 2): player_results = randomizer.choose(int(args[0]), int(args[1]))

        results_message = create_embed('Civilization Randomizer', 'Randomizer results for ' + args[0] + ' players.')
        for index, player in enumerate(player_results):
            player_string = ""
            for i, civ in enumerate(player):
                player_string = player_string + civ.name
                if(i != (len(player) - 1)): player_string = player_string + ", "

            results_message.add_field(name="Player " + str(index +  1) + ': (' + str(len(player)) + ' civs)', value=player_string, inline=False)
        await message.channel.send(embed=results_message)
    else: await deny_message(message)

async def display_blacklist(message, args):
    await confirm_message(message)
    result_message = create_embed('Civilization Randomizer', 'Randomizer blacklisted civilizations. These will be ommited when using ' + prefix + 'choose.')
    for civ in randomizer.blacklist: result_message.add_field(name=civ, value='Banned', inline=True)
    await message.channel.send(embed=result_message)

async def ban(message, args):
    if(len(args) >= 1):
        if(args[0] == 'all'):
            await confirm_message(message)
            for civ in randomizer.pool: randomizer.toggle_civ(civ.name, False)
        else:
            civs_recognized = True
            for arg in args:
                if(arg in randomizer.pool): randomizer.toggle_civ(args[0], False)
                else: civs_recognized = False
            if(civs_recognized): await confirm_message(message)
            else: await deny_message(message)
    else: await deny_message(message)

async def unban(message, args):
    if(len(args) >= 1):
        if(args[0] == 'all'):
            await confirm_message(message)
            for civ in randomizer.pool: randomizer.toggle_civ(civ.name, True)
        else:
            civs_recognized = True
            for arg in args:
                if(arg in randomizer.pool): randomizer.toggle_civ(args[0], True)
                else: civs_recognized = False
            if(civs_recognized): await confirm_message(message)
            else: await deny_message(message)
    else: await deny_message(message)

async def display_dlcs(message, args): pass

async def enable(message, args): pass

async def disable(message, args): pass

#
# Initialization
#
client = discord.Client()
randomizer = choose.CivRandomizer(verbose=True)
bot_token = os.getenv('CIV_BOT_TOKEN')

#
# Discord event stuff
#
@client.event
async def on_connect():
    user = client.user
    utils.log(0, "Logged in as " + str(user))

@client.event
async def on_disconnect():
    #
    # Band-aid fix to destructor issue of scope calls miraculously not working anymore as soon as the
    #   destructor is in scope, ergo files can no longer be opend and saved to
    #
    utils.log(0, "Logging out of discord...\n\tSaving choose profile to file: " + randomizer.config_path)
    utils.dump_json(randomizer.config_path, randomizer.profile)

@client.event
async def on_ready(): await set_default_status()

@client.event
async def on_typing(channel, user, when): pass

@client.event
async def on_message(message):
    pieces = message.content.split(" ")
    author = message.author
    command = pieces[0][2:]
    args = pieces[1:]

    if(message.content[:2] == prefix):
        utils.log(0, "Message from (" + str(author) + "): \"" + message.content + "\"")

        if(command == 'help'):
            await set_status('Getting help...')
            await usage(message)
        elif(command == 'choose'):
            await set_status('Choosing things...')
            await choose_civs(message, args)
        elif(command == 'blacklist'):
            await set_status('Getting banned things...')
            await display_blacklist(message, args)
        elif(command == 'ban'):
            await set_status('Banning things...')
            await ban(message, args)
        elif(command == 'unban'):
            await set_status('Unbanning things...')
            await unban(message, args)
        elif(command == 'dlcs'):
            await set_status('Getting DLC things...')
            await display_dlcs(message, args)
        elif(command == 'enable'):
            await set_status('Enabling DLC\'s...')
            await enable(message, args)
        elif(command == 'disable'):
            await set_status('Disabling DLC\'s...')
            await disable(message, args)
        else: await deny_message(message)

        await set_default_status()

client.run(bot_token)
