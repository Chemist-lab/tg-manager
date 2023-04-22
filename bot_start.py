# 23465764
# b0d09e5fdddd42e50eb821496550eb4c
from config import *

from database_manager import *

from admin_cms import *

from user_commands import *



from telethon.tl.functions.channels import GetFullChannelRequest

# creating client here


# chatinvite = client(CheckChatInviteRequest('https://t.me/+glAkOhlU30c1Y2Zi'))
# channel_id = chatinvite.chat.id

# with TelegramClient('session_name', api_id, api_hash) as client1:
#     for dialog in client1.iter_dialogs():
#         print(dialog)
#         if "Legion CumMander" in dialog.title:
#             break
        


# from test_commands import *

client.start()
client.run_until_disconnected()