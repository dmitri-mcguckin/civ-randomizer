import os
import shutil
import discord
import civ_randomizer as cr
import civ_randomizer.config_factory as cf


class Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.setup_config_cache()

        if(os.path.exists(cr.CONFIG_PATH)):
            config = cf.load_config(cr.CONFIG_PATH)
        else:
            config = cf.bot_config_factory()
            cf.save_config(cr.CONFIG_PATH, config)
        self.config = config

        self.default_profile = cf.load_config(cr.PROFILE_PATH)
        self.commands = cf.load_config(cr.COMMANDS_PATH)

    def setup_config_cache(self) -> None:
        os.makedirs(cr.CONFIG_DIR, exist_ok=True)
        os.makedirs(cr.CACHE_DIR, exist_ok=True)

        # Civ Profile
        if(not os.path.exists(cr.PROFILE_PATH)):
            shutil.copyfile('assets/civ-v-profile.json', cr.PROFILE_PATH)

        # Discord commands
        if(not os.path.exists(cr.COMMANDS_PATH)):
            shutil.copyfile('assets/discord-commands.json', cr.COMMANDS_PATH)

    async def handle_guild(self, guild: discord.Guild):
        cache_dir = '{}{}'.format(cr.CACHE_DIR, guild.id) + os.sep

        if(not os.path.exists(cache_dir)):
            os.makedirs(cache_dir)
            shutil.copyfile(cr.PROFILE_PATH, cache_dir + 'default-profile.json')

    async def handle_help(self, message):
        pass

    async def on_ready(self):
        guild_names = list(map(lambda x: x.name, self.guilds))
        print('Logged into discord as {}!\n\tIn these servers: {}'
              .format(self.user, guild_names))
        for guild in self.guilds:
            await self.handle_guild(guild)

    async def on_message(self, message):
        prefix = self.config['prefix']

        if(message.content.startswith(prefix)):
            print('Got message: {}'.format(message))

    def stop(self):
        print('shutting down bot...')
