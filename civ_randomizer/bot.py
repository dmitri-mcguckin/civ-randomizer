import os
import re
import shutil
import argparse
import discord
import civ_randomizer as cr
from civ_randomizer.randomizer import Randomizer
from discord.ext import commands


class CivRandomizerEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(title=cr.BOT_NAME.title(),
                         author=cr.BOT_NAME.title(),
                         descriptio=cr.BOT_DESCRIPTION,
                         url=cr.BOT_URL,
                         **kwargs)


class StatusContext(commands.Context):
    async def tick(self, ok: bool = None):
        emoji = {
            True: '\N{WHITE HEAVY CHECK MARK}',
            False: '\N{CROSS MARK}',
            None: 'N/A'
        }[ok]

        if(ok is None):  # If no status is provided, clear reactions
            await self.message.clear_reactions()
        else:  # Otherwise set the new reaction
            await self.tick()
            try:
                await self.message.add_reaction(emoji)
            except discord.HTTPException as e:
                cr.LOG.error(e)


class CivRandomizerBot(commands.Bot):
    def __init__(self, **kwargs):
        # Call the parent
        super().__init__('!', **kwargs)

        # Bot Defaults
        self.case_insensitive = True
        self.config = {}
        self.randomizers = {}

    def stop(self):
        cr.LOG.info('Saving bot config to {}...'
                    .format(cr.BOT_CONFIG))
        self.save_bot_config()

    async def on_guild_join(self, guild: discord.Guild):
        profile = self.load_profile(guild.id)
        self.randomizers[guild.id] = profile

    async def on_ready(self):
        cr.LOG.info('Logged in as user: {} in guilds: {}'.format(self.user, self.guilds))
        await self.reset_status()

        # Load the bot config
        self.load_bot_config()

        # Generate each guild cache dir
        for guild in self.guilds:
            profile = self.load_profile(guild.id)
            self.randomizers[guild.id] = Randomizer(profile)

    async def reset_status(self):
        activity = discord.Activity(name='{}help'.format(self.command_prefix),
                                    status='1',
                                    type=discord.ActivityType.playing)
        await self.change_presence(activity=activity)

    def load_bot_config(self, filename: str = cr.BOT_CONFIG):
        if(not os.path.exists(filename)):
            self.config = {'command_prefix': 'c!'}
            cr.LOG.warn('Config was expected at {}, but was not found!\n\t\
                         Will auto-generate it now with the defaults: {}'
                        .format(filename, self.config))
            os.makedirs(cr.OPT_DIR, exist_ok=True)
            cr.save_dict_to_json(self.config, filename)
        else:
            self.config = cr.load_dict_from_json(filename)

        for key, value in self.config.items():
            setattr(self, key, value)

    def save_bot_config(self, filename: str = cr.BOT_CONFIG):
        cr.save_dict_to_json(self.config, filename)

    def load_profile(self,
                     guild_id: int,
                     filename: str = cr.BOT_CURRENT_PROFILE) -> dict:
        filename = filename.format(guild_id)
        if(not os.path.exists(filename)):
            self.config = {'command_prefix': 'c!'}
            cr.LOG.warn('Profile was expected at {}, but was not found!\n\t\
                         Will auto-generate it now with the defaults: {}'
                        .format(filename, cr.DEFAULT_PROFILE_ASSET))
            os.makedirs(cr.BOT_PROFILES_DIR.format(guild_id),
                        exist_ok=True)
            shutil.copyfile(cr.DEFAULT_PROFILE_ASSET,
                            cr.BOT_CURRENT_PROFILE.format(guild_id))
        return cr.load_dict_from_json(filename)

    def save_profile(self,
                     guild_id: int,
                     profile: dict,
                     filename: str = cr.BOT_CURRENT_PROFILE) -> None:
        filename = filename.format(guild_id)
        cr.save_dict_to_json(profile, filename)

    async def get_context(self, message, *, cls=StatusContext):
        return await super().get_context(message, cls=cls)


# The bot
bot = CivRandomizerBot(description=cr.BOT_DESCRIPTION)


@bot.command(usage='<new prefix>',
             help='Set a new command prefix. (First character must be alpha-numeric)')
async def prefix(context: StatusContext):
    msg_parts = context.message.clean_content.split(' ')

    if(len(msg_parts) == 1):
        await context.tick(True)
        await context.send('Current prefix: "{}"'.format(bot.command_prefix))
    else:
        new_prefix = msg_parts[1]
        if(re.match('[a-zA-Z].*', new_prefix)):
            bot.command_prefix = new_prefix
            bot.config['command_prefix'] = new_prefix
            bot.save_bot_config()
            await bot.reset_status()
            await context.tick(True)
        else:
            await context.tick(False)


@bot.command(usage='<num players> <num civs per player: optional>',
             help='Randomly chooses a specified of civilizations per specified number of players.')
async def choose(context: StatusContext):
    args = context.message.clean_content.split(' ')[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('num_players',
                        type=int)
    parser.add_argument('--num-civs-per-player', '--ncpp',
                        dest='num_civs_per_player',
                        type=int,
                        default=1,
                        help='Number of civilizations per player for the randomizer.')
    parser.add_argument('--player-names', '--pn',
                        dest='player_names',
                        nargs='+',
                        default=None,
                        help='List of optional player names to map to selections. (The number of names must match the number of players or else this will be ignored).')
    try:
        args = parser.parse_args(args)
    except SystemExit as e:
        await context.tick(False)
        embed = CivRandomizerEmbed()
        embed.add_field(name='Error', value=str(e))
        await context.send(embed=embed)
        return

    # Get the guild-specific randomizer
    randomizer = bot.randomizers[context.guild.id]

    # Run the selection
    selection = randomizer.choose(args.num_players,
                                  args.num_civs_per_player,
                                  player_names=args.player_names)
    context.tick(True)

    # Load and send the embed payload
    embed = CivRandomizerEmbed()
    for name, civs in selection.items():
        civ_names = list(map(lambda x: x.name.title(), civs))
        embed.add_field(name=name.title(), value=', '.join(civ_names), inline=True)
    await context.send(embed=embed)


@bot.command(help='Gets the server-specific profile settings.')
async def profile(context: StatusContext):
    guild_id = context.guild.id
    randomizer = bot.randomizers[guild_id].to_dict()
    embed = CivRandomizerEmbed()
    context.tick(True)

    for key, value in randomizer.items():
        embed.add_field(name=key, value=str(value))
    await context.send(embed=embed)


@bot.command(help='Ban')
async def ban(context: StatusContext):
    guild_id = context.guild.id
    randomizer = bot.randomizers[guild_id]

    args = context.message.clean_content.split(' ')[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('civ',
                        type=str)
    try:
        args = parser.parse_args(args)
        randomizer.blacklist.append(args.civ.title())
        bot.save_profile(guild_id, randomizer.to_dict())
        await context.tick(True)
    except SystemExit as e:
        await context.tick(False)
        embed = CivRandomizerEmbed()
        embed.add_field(name='Error', value=str(e))
        await context.send(embed=embed)
        return


@bot.command(help='Unban')
async def unban(context: StatusContext):
    guild_id = context.guild.id
    randomizer = bot.randomizers[guild_id]

    args = context.message.clean_content.split(' ')[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('civ',
                        type=str)
    try:
        args = parser.parse_args(args)
        randomizer.blacklist.remove(args.civ.title())
        bot.save_profile(guild_id, randomizer.to_dict())
        await context.tick(True)
    except SystemExit as e:
        await context.tick(False)
        embed = CivRandomizerEmbed()
        embed.add_field(name='Error', value=str(e))
        await context.send(embed=embed)
        return
