from telethon import TelegramClient, events
from config import *
# We have to manually call "start" if we want an explicit bot token
client = TelegramClient('theker', api_id, api_hash).start(bot_token=bot_token)
print('Bot has been started')

async def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]