from config import *

from scripts.database_manager import *

from scripts.admin.admin_cms import *

from scripts.user.user_commands import *


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

