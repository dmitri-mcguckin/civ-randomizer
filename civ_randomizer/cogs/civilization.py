import os
import shutil
import math
import discord
import civ_randomizer as cr
from discord.ext import commands
from civ_randomizer.embed import Embed
from civ_randomizer.bot import CivRandomizerBot
from civ_randomizer.randomizer import Civilization, Randomizer
from civ_randomizer.status_context import StatusContext


class RandomizerCog(commands.Cog, name='Randomizer'):
    def __init__(self, bot: CivRandomizerBot):
        # Cog defaults
        self.bot = bot
        self.randomizers = {}

    def load_profile(self,
                     guild_id: int,
                     filename: str = cr.BOT_CURRENT_PROFILE) -> dict:
        filename = filename.format(guild_id)
        if(not os.path.exists(filename)):
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

    def generate_blacklist(self, randomizer: Randomizer) -> [Embed]:
        return self.generate_civilizations(randomizer.blacklist,
                                           banner='Blacklisted Civilizations',
                                           description='These civilizations will not show up in the draft pool even if its DLC pack is enabled.',
                                           color=discord.Color(0x000))

    def generate_civilizations(self,
                               civilizations: [Civilization],
                               banner='Vanilla Civilizations',
                               description='A list of the vanilla civs.',
                               color=discord.Color.green()) -> [Embed]:
        """
        Turns the given civilizations list into a list of sendable Discord Embeds
        """
        # The ammount of civilizations available might eclipse the maximum size
        #   of an embed, ergo: break it up into multiple embed payloads.
        embeds = []

        if(len(civilizations) > 0):
            slice_count = math.ceil(len(civilizations) / 36)
            slice_size = math.ceil(len(civilizations) / slice_count)
            slices = []

            for i in range(slice_count):
                start = i * slice_size
                end = start + slice_size
                slices.append(civilizations[start:end])

            for i, civ_slice in enumerate(slices):
                embed = Embed(title='{} ({}/{}) ({} civs)'
                                    .format(banner,
                                            i + 1,
                                            len(slices),
                                            len(civ_slice)),
                              description=description,
                              color=color)
                for civ in civ_slice:
                    aliases = ', '.join(civ.aliases)
                    if(aliases == '' or aliases is None):
                        aliases = 'No aliases'
                    embed.add_field(name=civ.name, value=aliases, inline=True)
                embeds.append(embed)
        else:
            embed = Embed(title='{}'.format(banner),
                          description=description,
                          color=color)
            embed.add_field(name='No Civs', value='N/A', inline=True)
            embeds.append(embed)
        return embeds

    def generate_dlcs(self, randomizer: Randomizer) -> Embed:
        """
        Turns the given randomizer dlcs list into a sendable Discord Embed
        """
        embed = Embed(title='Available DLC\'s',
                      description='This is a complete list of the default dlc\'s available.',
                      color=discord.Color.orange())
        for dlc in randomizer.dlc_packs:
            status = 'Enabled' if dlc.enabled else 'Disabled'
            civilizations = list(map(lambda x: x.name, dlc.civilizations))
            embed.add_field(name=dlc.name,
                            value='{}\nCivs: {}'
                                  .format(status, ', '.join(civilizations)),
                            inline=True)
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        # Generate each guild cache dir
        for guild in self.bot.guilds:
            profile = self.load_profile(guild.id)
            self.randomizers[guild.id] = Randomizer(profile)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        profile = self.load_profile(guild.id)
        self.randomizers[guild.id] = profile

    @commands.command(help=cr.COMMANDS['choose']['long'],
                      brief=cr.COMMANDS['choose']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def choose(self, context: StatusContext,
                     num_players: int,
                     civs_per_player: int = 5,
                     *, player_names: str = None):
        # Approve the context
        await context.tick(True)

        # If there is a string of player names, turn it into a list
        if(player_names is not None):
            player_names = player_names.split(' ')

        # Grab the guild-specific randomizer
        randomizer = self.randomizers[context.guild.id]

        # Run the selection
        selection = randomizer.choose(num_players,
                                      civs_per_player=civs_per_player,
                                      player_names=player_names)

        # Load and send the embed payload
        embed = Embed()
        for name, civs in selection.items():
            civ_names = sorted(list(map(lambda x: x.name.title(), civs)))
            embed.add_field(name=name.title(),
                            value=', '.join(civ_names),
                            inline=True)
        await context.send(embed=embed)

    @commands.command(help=cr.COMMANDS['profile']['long'],
                      brief=cr.COMMANDS['profile']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def profile(self, context: StatusContext):
        # Approve the context
        await context.tick(True)

        # Grab the guild-specific randomizer
        randomizer = self.randomizers[context.guild.id]

        # Create the blacklist embed(s) and send them
        for embed in self.generate_blacklist(randomizer):
            await context.send(embed=embed)

        # Create the civilization embed(s) and send them
        for embed in self.generate_civilizations(randomizer.civilizations):
            await context.send(embed=embed)

        # Create the dlcs embed and send it
        await context.send(embed=self.generate_dlcs(randomizer))

    @commands.command(help=cr.COMMANDS['blacklist']['long'],
                      brief=cr.COMMANDS['blacklist']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def blacklist(self, context: StatusContext):
        # Approve the context
        await context.tick(True)

        # Grab the guild-specific randomizer
        randomizer = self.randomizers[context.guild.id]

        # Create the dlcs embed and send it
        for embed in self.generate_blacklist(randomizer):
            await context.send(embed=embed)

    @commands.command(help=cr.COMMANDS['dlcs']['long'],
                      brief=cr.COMMANDS['dlcs']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def dlcs(self, context: StatusContext):
        # Approve the context
        await context.tick(True)

        # Grab the guild-specific randomizer
        randomizer = self.randomizers[context.guild.id]

        # Create the dlcs embed and send it
        await context.send(embed=self.generate_dlcs(randomizer))

    @commands.command(help=cr.COMMANDS['draft_pool']['long'],
                      brief=cr.COMMANDS['draft_pool']['short'],
                      aliases=['draftpool', 'pool'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def draft_pool(self, context: StatusContext):
        # Approve the context
        await context.tick(True)

        # Grab the guild-specific randomizer
        randomizer = self.randomizers[context.guild.id]

        # Create the civilizations embed and send it
        draft_pool = randomizer.generate_draft_pool()
        for embed in self.generate_civilizations(draft_pool,
                                                 banner='Draft Pool Civilizations',
                                                 description='A list of all actively draftable civilizations.'):
            await context.send(embed=embed)

    @commands.command(help=cr.COMMANDS['ban']['long'],
                      brief=cr.COMMANDS['ban']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def ban(self, context: StatusContext, civ: str):
        # Approve the context
        await context.tick(True)

        # Fetch the guild id and guild-specific randomizer
        guild_id = context.guild.id
        randomizer = self.randomizers[guild_id]

        # Add civ(s) to the blacklist and save the guild-specific profile
        if(civ == 'all'):
            randomizer.blacklist = sorted(randomizer.generate_draft_pool())
        else:
            ban_civ = randomizer.resolve_civ_name(civ)
            randomizer.blacklist.append(ban_civ)
        self.save_profile(guild_id, randomizer.to_dict())

    @commands.command(help=cr.COMMANDS['unban']['long'],
                      brief=cr.COMMANDS['unban']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def unban(self, context: StatusContext, civ: str):
        # Approve the context
        await context.tick(True)

        # Fetch the guild id and guild-specific randomizer
        guild_id = context.guild.id
        randomizer = self.randomizers[guild_id]

        # Remove civ(s) from the blacklist and save the guild-specific profile
        if(civ == 'all'):
            randomizer.blacklist = []
        else:
            unban_civ = randomizer.resolve_civ_name(civ)
            randomizer.blacklist.remove(unban_civ)
        self.save_profile(guild_id, randomizer.to_dict())

    @commands.command(help=cr.COMMANDS['enable']['long'],
                      brief=cr.COMMANDS['enable']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def enable(self, context: StatusContext, dlc: str):
        # Approve the context
        await context.tick(True)

        # Fetch the guild id and guild-specific randomizer
        guild_id = context.guild.id
        randomizer = self.randomizers[guild_id]

        # Enable the DLC(s) and save the guild-specific profile
        if(dlc.lower() == 'all'):
            randomizer.enable_all_dlc()
        else:
            randomizer.enable_dlc_by_name(dlc)
        self.save_profile(guild_id, randomizer.to_dict())

    @commands.command(help=cr.COMMANDS['disable']['long'],
                      brief=cr.COMMANDS['disable']['short'])
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def disable(self, context: StatusContext, dlc: str):
        # Approve the context
        await context.tick(True)

        # Fetch the guild id and guild-specific randomizer
        guild_id = context.guild.id
        randomizer = self.randomizers[guild_id]

        # Disable the DLC(s) and save the guild-specific profile
        if(dlc.lower() == 'all'):
            randomizer.disable_all_dlc()
        else:
            randomizer.disable_dlc_by_name(dlc)
        self.save_profile(guild_id, randomizer.to_dict())


def setup(bot: CivRandomizerBot):
    bot.add_cog(RandomizerCog(bot))
