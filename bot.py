from discord.ext.commands import Bot, CommandNotFound
from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor


cogs = ['cogs.tj',
        'cogs.botadmin']


class Gonabot(Bot):
    def __init__(self):
        super().__init__('.')
        self.threadpool = ThreadPoolExecutor(max_workers=2)
        self.client = ClientSession(loop=self.loop)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, CommandNotFound):
            return

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        for cog in cogs:
            self.load_extension(cog)
