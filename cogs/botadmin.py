import asyncio
import pprint
import shlex
import subprocess
import time
from importlib import reload, import_module

import discord
from discord.errors import HTTPException
from discord.ext.commands import command, is_owner

from cogs.cog import Cog


class BotAdmin(Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @command(name='eval')
    @is_owner()
    async def eval_(self, ctx, *, code: str):
        context = globals().copy()
        context.update({'ctx': ctx,
                        'author': ctx.author,
                        'guild': ctx.guild,
                        'message': ctx.message,
                        'channel': ctx.channel,
                        'bot': ctx.bot,
                        'loop': ctx.bot.loop})

        if '\n' in code:
            lines = list(filter(bool, code.split('\n')))
            last = lines[-1]
            if not last.strip().startswith('return'):
                whitespace = len(last) - len(last.strip())
                lines[-1] = ' ' * whitespace + 'return ' + last  # if code doesn't have a return make one

            lines = '\n'.join('    ' + i for i in lines)
            code = f'async def f():\n{lines}\nx = asyncio.run_coroutine_threadsafe(f(), loop).result()'  # Transform the code to a function
            local = {}  # The variables outside of the function f() get stored here

            try:
                await self.bot.loop.run_in_executor(self.bot.threadpool, exec, compile(code, '<eval>', 'exec'), context, local)
                retval = pprint.pformat(local['x'])
            except Exception as e:
                retval = f'{type(e).__name__}: {e}'

        else:
            try:
                retval = await self.bot.loop.run_in_executor(self.bot.threadpool, eval, code, context)
                if asyncio.iscoroutine(retval):
                    retval = await retval

            except Exception as e:
                retval = f'{type(e).__name__}: {e}'

        if not isinstance(retval, str):
            retval = str(retval)

        if len(retval) > 2000:
            await ctx.send(file=discord.File(retval, filename='result.txt'))
        else:
            await ctx.send(retval)

    @command(name='exec')
    @is_owner()
    async def exec_(self, ctx, *, message):
        context = globals().copy()
        context.update({'ctx': ctx,
                        'author': ctx.author,
                        'guild': ctx.guild,
                        'message': ctx.message,
                        'channel': ctx.channel,
                        'bot': ctx.bot})
        try:
            retval = await self.bot.loop.run_in_executor(self.bot.threadpool, exec, message, context)
            if asyncio.iscoroutine(retval):
                retval = await retval

        except Exception as e:
            retval = 'Exception\n%s' % e

        if not isinstance(retval, str):
            retval = str(retval)

        await ctx.send(retval)

    @command()
    @is_owner()
    async def reload(self, ctx, *, name):
        t = time.time()
        try:
            cog_name = 'cogs.%s' % name if not name.startswith('cogs.') else name

            def unload_load():
                self.bot.unload_extension(cog_name)
                self.bot.load_extension(cog_name)

            await self.bot.loop.run_in_executor(self.bot.threadpool, unload_load)
        except Exception as e:
                return await ctx.send('Could not reload %s because of an error\n%s' % (name, e))
        await ctx.send('Reloaded {} in {:.0f}ms'.format(name, (time.time()-t)*1000))

    @command()
    @is_owner()
    async def shutdown(self, ctx):
        try:
            await ctx.send('Shutting down')
        except HTTPException:
            pass

        try:
            pending = asyncio.Task.all_tasks(loop=self.bot.loop)
            gathered = asyncio.gather(*pending, loop=self.bot.loop)
            try:
                gathered.cancel()
                self.bot.loop.run_until_complete(gathered)

                # we want to retrieve any exceptions to make sure that
                # they don't nag us about it being un-retrieved.
                gathered.exception()
            except:
                pass

        except:
            pass
        finally:
            await self.bot.logout()

    @command()
    @is_owner()
    async def reload_module(self, ctx, module_name):
        try:
            reload(import_module(module_name))
        except Exception as e:
            return await ctx.send('Failed to reload module %s because of an error\n```%s```' % (module_name, e))
        await ctx.send('Reloaded module %s' % module_name)

    @command(ignore_extra=True)
    @is_owner()
    async def update_bot(self, ctx, *, options=None):
        """Does a git pull"""
        cmd = 'git pull'.split(' ')
        if options:
            cmd.extend(shlex.split(options))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = await self.bot.loop.run_in_executor(self.bot.threadpool, p.communicate)
        out = out.decode('utf-8')
        if err:
            out = err.decode('utf-8') + out

        if len(out) > 2000:
            out = out[:1996] + '...'

        await ctx.send(out)


def setup(bot):
    bot.add_cog(BotAdmin(bot))
