import bot
import json


with open('config.json') as f:
    config = json.load(f)

bot = bot.Gonabot()
bot.run(config['token'])
