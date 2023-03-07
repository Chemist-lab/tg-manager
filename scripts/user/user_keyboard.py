from scripts.function import *
from scripts.database_manager import *
from scripts.user.user_function import *

from telethon import Button

user_menu_state = {}

user_menu_selection_size = 5

async def usr_load_5_pic(event):
    who = event.sender_id
    _buttons = []

    nav = [Button.inline('<<', b"usr_mov_<<"),
           Button.inline('>>', b"usr_mov_>>")]


    print(user_menu_state[who])

    if await check_user(who) == False:
        await client.send_message(who,"У вас нет подписки")
        await event.answer("У вас нет подписки")
        return
# ORDER BY picture_access ASC
    cur.execute("SELECT * FROM image_list ORDER BY rowid DESC")
    _data = cur.fetchall()
    if len(_data) == 0:
        await client.send_message(who,"В базе данных нет фото")
        return
    


    lib_pos = user_menu_state[who]
    counter = 0

    active_lenth = 0
    for row in _data:
        if (row[2] == 'True'):
            active_lenth = active_lenth + 1

    for row in _data:
        if (row[2] == 'True'):
            if counter >= lib_pos:
                if counter >= lib_pos + user_menu_selection_size:
                     break
                name = row[1]
                name_id = f"{name}_{who}gi_usr_btn".encode("utf-8")
                _buttons.append(Button.inline(name, bytes(name_id)))
            counter = counter + 1

    _buttons = await convert_1d_to_2d(_buttons, 1)

    if active_lenth == counter:
        nav = [Button.inline('<<', b"usr_mov_<<")]
    if lib_pos == 0:
        nav = [Button.inline('>>', b"usr_mov_>>")]
    
    # if len(_buttons) == 0:
    #         msg = "В базе данных нет доступных фото."
    #         await client.edit_message(who, event.message_id, msg)
    #         await event.answer(msg)

    _buttons.append(nav)
    print(event.message_id)
    await client.edit_message(who, event.message_id, "Выберите фото", buttons = _buttons)



@client.on(events.CallbackQuery(data='usr_mov_<<'))
async def user_move_bkwrd(event):
    who = event.sender_id
    print(f'user menu state:    {user_menu_state[who]}')
    user_menu_state[who] = user_menu_state[who] - user_menu_selection_size
    await usr_load_5_pic(event)
    print(f'user menu state:    {user_menu_state[who]}')


@client.on(events.CallbackQuery(data='usr_mov_>>'))
async def user_move_frwrd(event):
    who = event.sender_id
    print(f'user menu state:    {user_menu_state[who]}')
    user_menu_state[who] = user_menu_state[who] + user_menu_selection_size
    print(f'user menu state:    {user_menu_state[who]}')
    await usr_load_5_pic(event)
        