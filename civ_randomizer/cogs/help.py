import civ_randomizer as cr
from discord.ext import commands
from civ_randomizer.embed import Embed
from civ_randomizer.status_context import StatusContext
from civ_randomizer.bot import CivRandomizerBot


class HelpCog(commands.Cog, name='Help'):
    def __init__(self, bot: CivRandomizerBot):
        self.bot = bot

    def resolve_command(self, cmd_name: str) -> commands.core.Command:
        for cmd in self.bot.commands:
            if(cmd.name.lower() == cmd_name.lower()):
                return cmd
            else:
                for alias in cmd.aliases:
                    if(alias.lower() == cmd_name):
                        return cmd
        return ValueError('Command not found: `{}`'.format(cmd_name))

    @commands.has_permissions(add_reactions=True, embed_links=True)
    @commands.command(help=cr.COMMANDS['help']['long'],
                      brief=cr.COMMANDS['help']['short'])
    async def help(self, context: StatusContext, cmd_name: str = None):
        # Approve the context
        await context.tick(True)

        # If no command is specified, list the short help menu
        if(cmd_name is None):
            for cog in self.bot.cogs.values():
                embed = Embed(title='Category: {}'.format(cog.qualified_name),
                              description=cog.description)

                for cmd in cog.walk_commands():
                    embed.add_field(name=cmd.name,
                                    value=cmd.brief,
                                    inline=False)
                await context.send(embed=embed)
        # If a command is specified print just its help menu
        else:
            # Grab the command by name, then  build the embed
            cmd = self.resolve_command(cmd_name)
            embed = Embed(title='Command: {}{}'
                                .format(self.bot.command_prefix, cmd.name),
                          description=cmd.help)

            # Add usage, if available
            if(len(cmd.clean_params) > 0):
                param_str = ''
                for param in cmd.clean_params.values():
                    param_str += '{}\n'.format(param.name)
                    param_str == '\n'
                embed.add_field(name='Parameters', value=param_str)

            # Add aliases, if available
            if(len(cmd.aliases) > 0):
                embed.add_field(name='Aliases', value=', '.join(cmd.aliases))

            # Add examples, if available
            examples = cr.COMMANDS[cmd.name]['examples']
            if(len(examples) > 0):
                example_str = ''
                for example in examples:
                    example_str += "`{}{}`\n" \
                                   .format(self.bot.command_prefix, example)
                embed.add_field(name='Examples', value=example_str)

            # Add the cog that the command is a member of then send it
            embed.add_field(name='Cog', value=cmd.cog.qualified_name)
            await context.send(embed=embed)


def setup(bot: CivRandomizerBot):
    bot.add_cog(HelpCog(bot))
