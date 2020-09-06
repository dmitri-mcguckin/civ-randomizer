import os
import shutil
import discord
import civ_randomizer as cr
from discord.ext import commands
from civ_randomizer.embed import Embed
from civ_randomizer.status_context import StatusContext


class CivRandomizerBot(commands.Bot):
    def __init__(self, **kwargs):
        # Call the parent so the bot behaves like a regular Discord bot
        super().__init__(None, **kwargs)

        # Bot Defaults
        self.case_insensitive = True
        self.cog_extensions = ['civ_randomizer.cogs.admin',
                               'civ_randomizer.cogs.civilization',
                               'civ_randomizer.cogs.help']

        # Remove the default help command
        self.remove_command('help')

        # Load all of the cogs
        for extension in self.cog_extensions:
            self.load_extension(extension)

    def stop(self):
        cr.LOG.info('Saving bot config to {}...'
                    .format(cr.BOT_CONFIG))
        self.save_bot_config()

    async def get_context(self, message, *, cls=StatusContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        cr.LOG.info('Logged in as {}'.format(self.user))
        cr.LOG.info('In Guilds:'.format(self.user))
        for guild in self.guilds:
            cr.LOG.info('\t- {}#{}'.format(guild.name, guild.id))

        # Load the bot's configs and help command details
        self.load_bot_config()

        # The command prefix might have changed so update the status to
        #   indicate that
        await self.reset_status()

    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def on_error(self, context: StatusContext, exception):
        await context.tick(False)

        embed = Embed(title='Internal Error',
                      description=str(exception),
                      url=cr.BOT_URLS['issues'],
                      color=discord.Color.dark_orange())
        await context.send(content='Internal error!\n\nPlease contact <@{}> about this, or create an **Issue:** (__<{}>__) on Github.'.format(cr.BOT_URLS['issues'])
                                   .format(cr.BOT_ADMIN_ID),
                           embed=embed)

    # @commands.has_permissions(add_reactions=True, embed_links=True)
    async def on_command_error(self,
                               context: StatusContext,
                               exception: Exception):
        await context.tick(False)

        if(context.command is not None):
            help_message = 'Try running `{}help {}` for usage and details.' \
                           .format(self.command_prefix, context.command)
        else:
            help_message = 'Try running `{}help` for usage and details.'\
                           .format(self.command_prefix)

        exception_msg = str(exception)
        cr.LOG.error(exception_msg)
        embed = Embed(title='User Input Error',
                      description='{}\n\n{}'
                                  .format(exception_msg, help_message),
                      url=cr.BOT_URLS['issues'],
                      color=discord.Color.red())
        await context.send(embed=embed)

    async def reset_status(self):
        activity = discord.Activity(name='{}help'.format(self.command_prefix),
                                    status='1',
                                    type=discord.ActivityType.playing)
        await self.change_presence(activity=activity)

    def to_dict(self):
        return {'command_prefix': self.command_prefix,
                'global_admins': self.global_admins}

    def load_bot_config(self, filename: str = cr.BOT_CONFIG):
        if(not os.path.exists(filename)):
            cr.LOG.warn('Config was expected at {}, but was not found!\n\t\
                         Will auto-generate it now with the defaults: {}'
                        .format(filename, cr.DEFAULT_CONFIG_ASSET))
            os.makedirs(cr.OPT_DIR, exist_ok=True)
            shutil.copyfile(cr.DEFAULT_CONFIG_ASSET, cr.BOT_CONFIG)
        config = cr.load_dict_from_json(filename)

        for key, value in config.items():
            setattr(self, key, value)

    def save_bot_config(self, filename: str = cr.BOT_CONFIG):
        cr.save_dict_to_json(self.to_dict(), filename)
