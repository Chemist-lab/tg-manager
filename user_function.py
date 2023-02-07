from pathlib import Path
from function import *
from database_manager import *


async def send_nudes(user_id, photo_name):
    if await check_user(user_id) == False:
        await client.send_message(user_id,"У вас нет подписки")
        return

    cur.execute("SELECT user_id, picture_name FROM bot_library WHERE user_id=? AND picture_name=?", (user_id, photo_name,))
    _data=cur.fetchall()
    if len(_data) == 0:
        cur.execute("SELECT rowid, * FROM bot_library WHERE user_id='0' AND picture_name=?", (photo_name,))
        _data=cur.fetchone()
        rowid_ = _data[0]
        cur.execute(f"UPDATE bot_library SET user_id='{user_id}' WHERE rowid='{rowid_}'")
        con.commit()

    cur.execute("SELECT picture_fullname FROM bot_library WHERE user_id=? AND picture_name=?", (user_id, photo_name))
    _data=cur.fetchall()
    picture_fullname = _data[0][0]
    photopath = f"{SAVE_FOLDER}{photo_name}/"

    for fn in Path(photopath).glob(f'{picture_fullname}.*'):
        photopath = fn
        print(fn)
    await client.send_file(user_id, file=f'{photopath}', force_document=True)


async def check_user(user_id):
    active_users = await client.get_participants(channel_id, aggressive=False, limit=2000)
    for i in active_users:
        if int(user_id) == int(i.id):
            return True
        
    else: return False