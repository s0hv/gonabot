from discord.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @property
    def bot(self):
        return self._bot
