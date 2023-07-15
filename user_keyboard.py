from function import *
from database_manager import *
from user_function import *

from telethon import Button

user_menu_state = {}

user_menu_selection_size = 8

user_full_menu_list = {}



async def usr_load_5_pic(event):
    who = event.sender_id
    _buttons = []

    nav = [Button.inline('<<', b"usr_mov_<<"),
           Button.inline('>>', b"usr_mov_>>")]


    
# ORDER BY picture_access ASC
    # cur.execute("SELECT * FROM image_list ORDER BY rowid DESC")
    # _data = cur.fetchall()
    # if len(_data) == 0:
    #     await client.send_message(who,"В базе 0.
    # данных нет фото")
    #     return
    
    _data = user_full_menu_list[who]

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


                date = get_date1(name)
                name_arr = name.split("_")
                name_arr.pop(len(name_arr)-1)
                name_arr.pop(len(name_arr)-1)
                name_arr.pop(len(name_arr)-1)
                new_name = ''
                for n in name_arr:
                    new_name = f"{new_name} {n}"
                new_name = f"{new_name} - {date}"

                    
                name_id = f"{name}_{who}gi_usr_btn".encode("utf-8")
                print(name_id)
                _buttons.append(Button.inline(new_name, bytes(name_id)))
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

    sort_date = ["Сортировать 1..9", "Сортировать 9..1"]
    sort_name = ["Сортировать A-Z", "Сортировать Z-A"]

    if user_full_menu_list[f"{who} revnum="] == True: sort_date = sort_date[0]
    else: sort_date = sort_date[1]
    
    if user_full_menu_list[f"{who} revname="] == True: sort_name = sort_name[0]
    else: sort_name = sort_name[1]

    sort_btns = [Button.inline(sort_name, b"sort_a_z"), Button.inline(sort_date, b"sort_1..9")]
    
    _buttons.append(nav)
    _buttons.append(sort_btns)
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
        

@client.on(events.CallbackQuery(data='sort_1..9'))
async def sorting_1_9(event):
    who = event.sender_id
    _data = user_full_menu_list[who]
    
    if user_full_menu_list[f"{who} revnum="] == False:
        user_full_menu_list[f"{who} revnum="]  = True
        _data.sort(reverse=True, key=get_date)
    else:
        user_full_menu_list[f"{who} revnum="] = False
        _data.sort(key=get_date)

    user_full_menu_list[who]=_data
    await usr_load_5_pic(event)


@client.on(events.CallbackQuery(data='sort_a_z'))
async def sorting_1_9(event):
    who = event.sender_id
    _data = user_full_menu_list[who]
    
    if user_full_menu_list[f"{who} revname="] == False:
        user_full_menu_list[f"{who} revname="]  = True
        _data.sort(reverse=True, key=get_name)
    else:
        user_full_menu_list[f"{who} revname="] = False
        _data.sort(key=get_name)

    user_full_menu_list[who]=_data
    await usr_load_5_pic(event)


def get_name(item):
    return item[1]

def get_date(item):
    res = get_date1(item[1])
    # print(res)
    return res

def get_date1(string):
        lenth = len(string)
        try:
            string = string[lenth-10 :]
            arr1 = string.split("_")
            if len(arr1) == 4:
                arr1.pop(0)
            if len(arr1[2]) == 4:
                arr1[2] = arr1[2][2:]

            string = f"20{arr1[2]}-{arr1[1]}-{arr1[0]}"

        except:
            string = '2000-01-01'
        return string