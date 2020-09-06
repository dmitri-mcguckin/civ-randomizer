import discord
import civ_randomizer as cr
from discord.ext import commands


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
