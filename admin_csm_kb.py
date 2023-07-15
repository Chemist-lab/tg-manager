from function import *
from database_manager import *

from telethon import Button

admin_menu_state = {}

admin_menu_selection_size = 12

async def admin_load_pic_table(event, chats=BOT_ADMIN_ID):
    who = event.sender_id
    
    print(who)
    _buttons = []

    nav = [Button.inline('<<', b"ad_mov_<<"),
           Button.inline('>>', b"ad_mov_>>")]


    print(admin_menu_state[who])

# ORDER BY picture_access ASC
    cur.execute("SELECT * FROM image_list ORDER BY rowid DESC")
    _data = cur.fetchall()
    if len(_data) == 0:
        await client.send_message(who,"В базе данных нет фото")
        return
    


    lib_pos = admin_menu_state[who]
    counter = 0

    active_lenth = 0
    for row in _data:
        if (row[2] is not None):
            active_lenth = active_lenth + 1

    for row in _data:
        if (row[2] is not None):
            if counter >= lib_pos:
                if counter >= lib_pos + admin_menu_selection_size:
                     break
                name = row[1]
                name_id = f"{name}_{who}gi_ad_btn".encode("utf-8")
                _buttons.append(Button.inline(name, bytes(name_id)))
            counter = counter + 1

    _buttons = await convert_1d_to_2d(_buttons, 1)

    if active_lenth == counter:
        nav = [Button.inline('<<', b"ad_mov_<<")]
    if lib_pos == 0:
        nav = [Button.inline('>>', b"ad_mov_>>")]
    
    # if len(_buttons) == 0:
    #         msg = "В базе данных нет доступных фото."
    #         await client.edit_message(who, event.message_id, msg)
    #         await event.answer(msg)

    _buttons.append(nav)
    print(event.message_id)
    await client.edit_message(who, event.message_id, "Выберите фото", buttons = _buttons)



@client.on(events.CallbackQuery(data='ad_mov_<<', chats=BOT_ADMIN_ID))
async def ad_move_bkwrd(event):
    who = event.sender_id
    print(f'admin menu state:    {admin_menu_state[who]}')
    admin_menu_state[who] = admin_menu_state[who] - admin_menu_selection_size
    await admin_load_pic_table(event)
    print(f'admin menu state:    {admin_menu_state[who]}')


@client.on(events.CallbackQuery(data='ad_mov_>>', chats=BOT_ADMIN_ID))
async def ad_move_frwrd(event):
    who = event.sender_id
    print(f'admin menu state:    {admin_menu_state[who]}')
    admin_menu_state[who] = admin_menu_state[who] + admin_menu_selection_size
    print(f'admin menu state:    {admin_menu_state[who]}')
    await admin_load_pic_table(event)
        


