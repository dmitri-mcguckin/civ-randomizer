import discord
import copy
import os
from time import ctime
import civ_randomizer.randomizer as randomizer


class CivBot(discord.Client):
    def __init__(self, token,
                       commands,
                       default_profile,
                       conf,
                       verbose = False,
                       prefix = "c!",
                       message = "Twiddling thumbs...",
                       website = "https://github.com/dmitri-mcguckin/civ-randomizer",
                       color = 0x7625d9):
        super().__init__()
        self.token = token
        self.default_profile = default_profile
        self.cache_dir = conf[1]
        self.verbose = verbose
        self.commands = commands
        self.prefix = prefix
        self.message = message
        self.website = website
        self.color = color
        self.randomizers = {}

        CivBot.LOG_DIR = conf[0]

    # Static functions
    def log_file(mode, msg):
        log(mode, msg)

        if(mode == Mode.INFO): log_path = CivBot.LOG_DIR + os.sep + 'info.log'
        elif(mode == Mode.WARN): log_path = CivBot.LOG_DIR + os.sep + 'warn.log'
        elif(mode == Mode.DEBUG): log_path = CivBot.LOG_DIR + os.sep + 'debug.log'
        elif(mode == Mode.ERROR): log_path = CivBot.LOG_DIR + os.sep + 'error.log'
        else: log_path = CivBot.LOG_DIR + os.sep + 'misc.log'

        file = open(log_path, 'a')
        file.write("[" + ctime() + "]: " + msg + "\n")
        file.close()

    async def confirm_message(message): await message.add_reaction(CONFIRM_EMOJI)
    async def deny_message(message): await message.add_reaction(DENY_EMOJI)

    # Instance functions
    def run(self): super().run(self.token)

    def randomizer(self, guild):
        if(guild not in self.guilds): raise Exception("Guild does not exist: " + str(guild) + " [" + str(guild.id) + "]")
        return self.randomizers[int(guild.id)]

    def load_profile(self, guild):
        profile_path = self.cache_dir + os.sep + str(guild.id) + '_guild.json'
        if(os.path.exists(profile_path)): profile = load_json(profile_path)
        else: profile = self.default_profile
        self.randomizers[int(guild.id)] = copy.deepcopy(randomizer.Randomizer(profile, verbose = self.verbose))

    def dump_profile(self, guild):
        profile_path = self.cache_dir + os.sep + str(guild.id) + '_guild.json'
        dump_json(profile_path, self.randomizers[int(guild.id)].profile)

    def clear_profile(self, guild):
        profile_path = self.cache_dir + os.sep + str(guild.id) + '_guild.json'
        if(os.path.exists(profile_path)): os.remove(profile_path)
        del self.randomizers[int(guild.id)]

    def create_embed(self, title, description, author = None):
        if(author is None): author = self.user.name
        embed = discord.Embed(title = title,
                              description = description,
                              url = self.website,
                              color = self.color)
        embed.set_author(name = author,
                         url = self.website)
        return embed

    async def usage(self, message):
        await CivBot.confirm_message(message)
        usage_msg = self.create_embed('Civilization Randomizer Bot', 'General usage and commands.')

        for command, data in self.commands.items():
            if(data[0] != ""): usage_msg.add_field(name = self.prefix + command + " [" + data[0] + "]",
                                                   value = data[1],
                                                   inline = False)
            else: usage_msg.add_field(name = self.prefix + command,
                                      value = data[1],
                                      inline = False)

        await message.channel.send(embed = usage_msg)

    async def set_default_status(self):
        await self.set_status(self.prefix + "help | " + self.message, status=discord.Status.idle)

    async def set_status(self, message, status = discord.Status.online):
        await self.change_presence(status = status, activity = discord.Game(message))

    async def display_civs(self, guild, message, args):
        await CivBot.confirm_message(message)

        # The civilization list is so big it needs to be split up into two payloads to fit into sendable embeds
        self.randomizer(guild).pool.sort()
        half_list = int(len(self.randomizer(guild).pool) / 2)
        result_message_1 = self.create_embed('Civilization Randomizer', '[1/2] A full list of civilizations in finer detail.')
        result_message_2 = self.create_embed('Civilization Randomizer', '[2/2] A full list of civilizations in finer detail.')

        for civ in self.randomizer(guild).pool[:half_list]:
            status = '[Disabled]'
            dlc_string = ""
            aka_string = "No aliases"
            if(civ.is_dlc): dlc_string = "<DLC>"
            if(civ.enabled): status = '[Enabled]'
            if(len(civ.alternate_names) > 0):
                aka_string = "Also known as: "
                for index, name in enumerate(civ.alternate_names):
                    aka_string = aka_string + name
                    if(index != (len(civ.alternate_names) - 1)): aka_string = aka_string + ', '
            result_message_1.add_field(name=civ.name + ' ' + dlc_string + ' ' + status, value=aka_string, inline=False)

        for civ in self.randomizer(guild).pool[half_list:]:
            status = '[Disabled]'
            dlc_string = ""
            aka_string = "No aliases"
            if(civ.is_dlc): dlc_string = "<DLC>"
            if(civ.enabled): status = '[Enabled]'
            if(len(civ.alternate_names) > 0):
                aka_string = "Also known as: "
                for index, name in enumerate(civ.alternate_names):
                    aka_string = aka_string + name
                    if(index != (len(civ.alternate_names) - 1)): aka_string = aka_string + ', '
            result_message_2.add_field(name=civ.name + ' ' + dlc_string + ' ' + status, value=aka_string, inline=False)

        await message.channel.send(embed=result_message_1)
        await message.channel.send(embed=result_message_2)

    async def choose_civs(self, guild, message, args):
        player_results = []

        if(len(args) == 1 or len(args) == 2):
            CivBot.log_file(Mode.INFO, "Got argument(s) for choose: " + str(args))

            try:
                for arg in args: int(arg)
            except ValueError as e:
                await CivBot.deny_message(message)
                CivBot.log_file(Mode.WARN, str(e) + "\n\tGracefully skipping processing this command.")
                return

            await CivBot.confirm_message(message)

            if(len(args) == 1): player_results = self.randomizer(guild).choose(int(args[0]))
            elif(len(args) == 2): player_results = self.randomizer(guild).choose(int(args[0]), int(args[1]))

            results_message = self.create_embed('Civilization Randomizer', 'Randomizer results for ' + args[0] + ' players.')
            for index, player in enumerate(player_results):
                player_string = ""
                for i, civ in enumerate(player):
                    player_string = player_string + civ.name
                    if(i != (len(player) - 1)): player_string = player_string + ", "

                results_message.add_field(name="Player " + str(index +  1) + ': (' + str(len(player)) + ' civs)', value=player_string, inline=False)
            await message.channel.send(embed=results_message)
        else: await CivBot.deny_message(message)

    async def display_blacklist(self, guild, message, args):
        await CivBot.confirm_message(message)
        result_message = self.create_embed('Civilization Randomizer', 'Randomizer blacklisted civilizations. These will be ommited when using ' + self.prefix + 'choose.')
        for civ in self.randomizer(guild).blacklist: result_message.add_field(name=civ, value='Banned', inline=True)
        await message.channel.send(embed=result_message)

    async def ban(self, guild, message, args):
        if(len(args) >= 1):
            if(args[0] == 'all'):
                await CivBot.confirm_message(message)
                for civ in self.randomizer(guild).pool: self.randomizer(guild).toggle_civ(civ.name, False)
            else:
                civs_recognized = True
                for arg in args:
                    if(arg in self.randomizer(guild).pool): self.randomizer(guild).toggle_civ(args[0], False)
                    else: civs_recognized = False
                if(civs_recognized): await CivBot.confirm_message(message)
                else: await CivBot.deny_message(message)
        else: await CivBot.deny_message(message)

    async def unban(self, guild, message, args):
        if(len(args) >= 1):
            if(args[0] == 'all'):
                await CivBot.confirm_message(message)
                for civ in self.randomizer(guild).pool: self.randomizer(guild).toggle_civ(civ.name, True)
            else:
                civs_recognized = True
                for arg in args:
                    if(arg in self.randomizer(guild).pool): self.randomizer(guild).toggle_civ(args[0], True)
                    else: civs_recognized = False
                if(civs_recognized): await CivBot.confirm_message(message)
                else: await CivBot.deny_message(message)
        else: await CivBot.deny_message(message)

    async def display_dlcs(self, guild, message, args):
        await CivBot.confirm_message(message)
        result_message = self.create_embed('Civilization Randomizer', 'A list of all available DLC\'s for Sid Meyer\'s Civilization V.')
        for dlc_name, dlc_data in self.randomizer(guild).profile['dlc_packs'].items():
            status = 'Disabled'
            civ_string = "Includes: "
            for index, civ in enumerate(dlc_data['civs'].keys()):
                civ_string = civ_string + civ
                if(index != (len(dlc_data['civs'].keys()) - 1)): civ_string = civ_string + ', '
            if(dlc_data['enabled']): status = 'Enabled'
            result_message.add_field(name=dlc_name + ' [' + status + ']', value=civ_string, inline=False)
        await message.channel.send(embed=result_message)

    async def enable(self, guild, message, args):
        if(len(args) >= 1):
            if(args[0] == 'all'):
                await CivBot.confirm_message(message)
                for dlc in self.randomizer(guild).profile['dlc_packs'].keys(): self.randomizer(guild).toggle_dlc(dlc, True)
            else:
                await CivBot.confirm_message(message)
                for arg in args: self.randomizer(guild).toggle_dlc(arg, True)
        else: await CivBot.deny_message(message)

    async def disable(self, guild, message, args):
        if(len(args) >= 1):
            if(args[0] == 'all'):
                await CivBot.confirm_message(message)
                for dlc in self.randomizer(guild).profile['dlc_packs'].keys(): self.randomizer(guild).toggle_dlc(dlc, False)
            else:
                await CivBot.confirm_message(message)
                for arg in args: self.randomizer(guild).toggle_dlc(arg, False)
        else: await CivBot.deny_message(message)

    async def on_ready(self):
        CivBot.log_file(Mode.INFO, "Logged in as " + str(self.user))
        await self.set_default_status()

        CivBot.log_file(Mode.INFO, "Guilds: ")
        for guild in self.guilds:
            CivBot.log_file(Mode.INFO, "\t" + str(guild) + "[" + str(guild.id) + "]")
            self.load_profile(guild)
            self.dump_profile(guild)

    async def on_disconnect(self):
        CivBot.log_file(Mode.WARN, "Shutting down Civ Randomizer!")
        for guild_id in self.randomizers.keys(): self.dump_profile(guild_id)

    async def on_guild_join(self, guild): self.load_profile(guild)
    async def on_guild_remove(self, guild): self.clear_profile(guild)

    async def on_message(self, message):
        pieces = message.content.split(" ")
        author = message.author
        guild = message.guild
        command = pieces[0][2:]
        args = pieces[1:]

        if(message.content[:2] == self.prefix):
            CivBot.log_file(Mode.INFO, "Message from (" + str(author) + ") in [" + str(guild) + "(" + str(guild.id) + ")]: \"" + message.content + "\"")

            if(command == 'help'):
                await self.set_status('Getting help...')
                await self.usage(message)
            elif(command == 'civs'):
                await self.set_status('Getting civ pool...')
                await self.display_civs(guild, message, args)
            elif(command == 'blacklist'):
                await self.set_status('Getting blacklist...')
                await self.display_blacklist(guild, message, args)
            elif(command == 'ban'):
                await self.set_status('Banning civ...')
                await self.ban(guild, message, args)
            elif(command == 'unban'):
                await self.set_status('Unbanning civ...')
                await self.unban(guild, message, args)
            elif(command == 'choose'):
                await self.set_status('Choosing civs...')
                await self.choose_civs(guild, message, args)
            elif(command == 'dlcs'):
                await self.set_status('Getting dlc pool...')
                await self.display_dlcs(guild, message, args)
            elif(command == 'enable'):
                await self.set_status('Enabling dlc...')
                await self.enable(guild, message, args)
            elif(command == 'disable'):
                await self.set_status('Disabling dlc...')
                await self.disable(guild, message, args)
            else: await CivBot.deny_message(message)

            self.dump_profile(guild)
            await self.set_default_status()
