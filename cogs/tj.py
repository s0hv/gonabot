from cogs.cog import Cog
from discord.ext.commands import command, cooldown


class TJ(Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @command()
    async def tj(self):