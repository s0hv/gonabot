from cogs.cog import Cog
from discord.ext.commands import command, cooldown, BadArgument
from bs4 import BeautifulSoup
from discord import Embed
import json
from datetime import datetime


def convert_class(s):
    try:
        group, year, = s.split('/')
    except ValueError:
        raise BadArgument(f"Couldn't convert {s} to correct format. Use format I/18")

    g = group
    group = group.replace('1', 'I').upper()
    group = group.replace('2', 'II')
    if len(group) > 2 or group not in ('I', 'II'):
        raise BadArgument(f'{g} must be I or II')

    try:
        int(year)
    except ValueError:
        raise BadArgument("Could not convert year to an integer")

    if len(year) != 2:
        raise BadArgument('Year must be shortened version of the year e.g. 18')

    return f'{group}/{year}'


def convert_dur(i):
    try:
        i = int(i)
    except ValueError:
        raise BadArgument(f'Could not convert {i} to integer')

    if i not in (165, 255, 347):
        raise BadArgument(f'{i} must be one of 165, 255, 347')

    return i


class TJ(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        with open('pokemon.json', 'r', encoding='utf-8') as f:
            self.pokemon = json.load(f)

    @command()
    async def tj(self, ctx, saapumisera: convert_class='I/18', pituus: convert_dur=255):
        url = f'http://tjlaskuri.fi/?s={saapumisera}&p={pituus}'
        async with self.bot.client.get(url) as r:
            print(r.status)
            if r.status != 200:
                return await ctx.send('TJ:n haku epäonnistui')

            soup = BeautifulSoup(await r.text(encoding='utf-8'), 'lxml')

        tj = soup.find('span', attrs={'id': 'tj'})
        div = soup.find('div', attrs={'id': "saapumisera"})
        era = div.find('div', attrs={'class': 'selected'})
        if era.text != saapumisera:
            return await ctx.send('Virheellinen saapumiserä')

        tj = int(tj.text.replace(',', ''))
        if tj > 0:
            if tj <= 151:
                tj_text = str(tj) if tj != 100 else ':100:'
                poke = self.pokemon.get(str(tj))
                embed = Embed(title=f'Tänään jäljellä {tj_text} aamua',
                              description=f'Päivän pokemon {poke["name"]}')
                embed.set_image(url='http://assets22.pokemon.com/assets/cms2/img/pokedex/full/%s.png' % str(tj).zfill(3))
                await ctx.send(embed=embed)
            else:
                text = f'Tänään jäljellä {tj} aamua'
                if tj == pituus:
                    astuminen = soup.find('td', attrs={'id': 'astuminen'}).text
                    astuminen = datetime.strptime(astuminen, '%d.%m.%Y')
                    current = datetime.utcnow()
                    if astuminen.year == current.year and astuminen.month == current.month and astuminen.day == current.day:
                        pass
                    # Service hasn't started yet
                    elif astuminen.year > current.year or (astuminen.year == current.year and (astuminen.month > current.month or (astuminen.month == current.month and astuminen.day > current.day))):
                        text = 'Palvelukseen astumiseen {} päivää'.format((astuminen - current).days + 1)
                    else:
                        pass

                await ctx.send(text)

        elif tj == 0:
            await ctx.send('Reserviin POISTU!')
        elif tj < 0:
            await ctx.send(f'Kotiutumisesta {abs(tj)} aamua 🌞')


def setup(bot):
    bot.add_cog(TJ(bot))
