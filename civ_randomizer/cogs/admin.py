import civ_randomizer as cr
from discord.ext import commands
from civ_randomizer.bot import CivRandomizerBot
from civ_randomizer.status_context import StatusContext


class AdminCog(commands.Cog, name='Global Admin'):
    def __init__(self, bot: CivRandomizerBot):
        self.bot = bot

    # def cog_check(self, context: StatusContext):
    #     return context.author.id in self.bot.global_admins

    @commands.has_permissions(add_reactions=True, embed_links=True)
    @commands.command(help=cr.COMMANDS['prefix']['long'],
                      brief=cr.COMMANDS['prefix']['short'])
    async def prefix(self, context: StatusContext, new_prefix: str):
        # Approve the context
        await context.tick(True)

        # Set the new prefix and update the config file
        self.bot.command_prefix = new_prefix
        self.bot.save_bot_config()

        # Reset the bot's global status
        await self.bot.reset_status()


def setup(bot: CivRandomizerBot):
    bot.add_cog(AdminCog(bot))
