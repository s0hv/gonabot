from discord.ext.commands import Bot
from aiohttp import ClientSession


cogs = ['cogs.tj']


class Gonabot(Bot):
    def __init__(self):
        super().__init__('.')
        self.client = ClientSession(loop=self.loop)
