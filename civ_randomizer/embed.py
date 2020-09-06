import discord
import civ_randomizer as cr


class Embed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(title=kwargs.get('title')
                         if kwargs.get('title') is not None
                         else cr.BOT_NAME.title(),

                         author=kwargs.get('author')
                         if kwargs.get('author') is not None
                         else cr.BOT_NAME.title(),

                         description=kwargs.get('description')
                         if kwargs.get('description') is not None
                         else cr.BOT_DESCRIPTION,

                         url=kwargs.get('url')
                         if kwargs.get('url') is not None
                         else cr.BOT_URLS['home'],

                         color=kwargs.get('color')
                         if kwargs.get('color') is not None
                         else discord.Color.dark_blue())
