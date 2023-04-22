from enum import Enum, auto

from PIL import Image, ImageFont, ImageDraw 

import shutil

import os

from pathlib import Path

from telethon import events
from telethon.tl.custom import Button

from config import *
from function import *
from database_manager import *
from user_function import create_and_send_photo_with_watermark


#ADMIN CMS FSM
class CreateDeletePhotoPackState(Enum):
    SEND_IMAGE = auto()
    IMAGE_NEW_NAME = auto()
    IMAGE_WATERMARK_SETTINNG = auto()
    IMAGES_COUNT = auto()

    START_DELETING_IMAGE = auto()
    SELECT_IMAGE_TO_DELETE = auto()
    CONFIRM_DELETING_SELECTED_IMAGE = auto()

class EditPhotoPackState(Enum):
    SELECT_IMAGE = auto()
    SELECT_OPTION = auto()
    IMAGE_NEW_NAME = auto()
    IMAGE_WATERMARK_SETTINNG = auto()

class GetUserByPhonoNumberState(Enum):
    SELECT_IMAGE = auto()
    SELECT_NUMBER_ON_PICTURE = auto()

class SetImageAccessState(Enum):
    SELECT_IMAGE = auto()
    SET_IMAGE_ACCESS = auto()

# The state in which different users are, {user_id: state}
admin_state = {}

admin_state_memory = {}

@client.on(events.NewMessage(pattern='/admin', chats=BOT_ADMIN_ID))
async def admin_command(event):
    msg = """
/createphoto
/deletephoto
/editphoto
/pacsess
/getuserbyphoto
/library
"""
    await event.respond(msg)

@client.on(events.NewMessage(pattern='/cancel', chats=BOT_ADMIN_ID))
async def admin_FSM_refresh(event):
    del admin_state[event.sender_id]
    await event.respond('Cостояние сброшено!')

# UPLOAD NEW IMAGE
@client.on(events.NewMessage(chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = admin_state.get(who)   

    if event.raw_text == '/createphoto':
        if state is None:
            await event.respond('Отправьте фото')
            admin_state[who] = CreateDeletePhotoPackState.SEND_IMAGE

    elif state == CreateDeletePhotoPackState.SEND_IMAGE:
        admin_state_memory[f'inp_path_{who}'] = str(await event.download_media(TG_SAVE_PATH))
        await event.respond('Хорошо! Задайте имя фото:')
        admin_state[who] = CreateDeletePhotoPackState.IMAGE_WATERMARK_SETTINNG

    elif state == CreateDeletePhotoPackState.IMAGE_WATERMARK_SETTINNG:
        wrong = ['/', '"\"']
        for wr in wrong:
            if wr in event.text:
                await event.respond('Недопустимые символы в названии!\nПопробуйте ещё раз:')
                state == CreateDeletePhotoPackState.SEND_IMAGE
                return
        
        admin_state_memory[f'image_new_name_{who}'] = event.text
        msg = """
Хорошо! Ведите параметры расположения и цвета ватермарки.
x y/hex/a/scale
x, y - звдиг по пикселям от верхнего левого угла.
hex - цвет в hex.
a - прозрачность текста (0-100).
scale - размер текста (0, 1, 2, ...).
Пример: 100 20/00ff00/70/50
"""

        await event.respond(msg)
        admin_state[who] = CreateDeletePhotoPackState.IMAGE_NEW_NAME

    elif state == CreateDeletePhotoPackState.IMAGE_NEW_NAME:

        path = admin_state_memory[f'inp_path_{who}']
        image_new_name = admin_state_memory[f'image_new_name_{who}']
        params =  event.text

        res = (await save_photo_to_lib(who, image_new_name, params, path))
        await create_and_send_photo_with_watermark(user_id=who, image_name=image_new_name, msg_id=0, t_text='0', mode=3)
        msg = """
Изображение успешно добавлено!

Для того, чтобы отредактировать ватермарку напишите: /editphoto

Для того, чтобы открыть доступ до изображения напишите: /pacsess
        """
        await client.send_message(who, msg)
        
        del admin_state[who]
        del admin_state_memory[f'inp_path_{who}']
        del admin_state_memory[f'image_new_name_{who}']



async def save_photo_to_lib(_user_id, _picture_name, _params, _image_path):
    cur.execute("SELECT * FROM image_list WHERE picture_name=?", (_picture_name,))
    _data=cur.fetchall()
    if len(_data) != 0:
        return 2
    cur.execute(f"INSERT INTO image_list VALUES ('{_user_id}', '{_picture_name}', 'False', '{_params}', '{_image_path}')")
    con.commit()
    return 0


@client.on(events.NewMessage(pattern='/deletephoto', chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    cur.execute("SELECT * FROM image_list")
    _data = cur.fetchall()

    _buttons = []
    if len(_data) == 0:
        await client.send_message(who,"В базе данных нет фото")
        return

    for row in _data:
        name = row[1]
        name_id = f"{name}_{who}_gi_del_a_b".encode("utf-8")
        _buttons.append(Button.inline(name, bytes(name_id)))

    _buttons = await convert_1d_to_2d(_buttons, 2)

    await client.send_message(who,"Выберите фото пак для удаления:", buttons = _buttons)

    admin_state[who] = CreateDeletePhotoPackState.SELECT_IMAGE_TO_DELETE


# GET USER BY IMAGE ID
@client.on(events.NewMessage(chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = admin_state.get(who)
    print(f'Admin state for {who}: {state}')

    if event.raw_text == '/getuserbyphoto':
        if state is None:
            cur.execute("SELECT * FROM image_list")
            _data = cur.fetchall()

            _buttons = []
            if len(_data) == 0:
                await client.send_message(who,"В базе данных нет фото")
                return

            for row in _data:
                name = row[1]
                name_id = f"{name}_get_user_by_image_admin_btn".encode("utf-8")
                _buttons.append(Button.inline(name, bytes(name_id)))

            _buttons = await convert_1d_to_2d(_buttons, 3)

            await client.send_message(who,"Выберите фото", buttons= _buttons)
            
            admin_state[who] = GetUserByPhonoNumberState.SELECT_IMAGE

    elif state == GetUserByPhonoNumberState.SELECT_NUMBER_ON_PICTURE:
        image_num = event.raw_text
        
        photo_name = admin_state_memory[f'get_image_name_state_{who}']

        cur.execute("SELECT user_id FROM bot_library WHERE picture_name=? AND picture_pos=?", (photo_name, image_num,))
        _data=cur.fetchall()
        print(f"\n\n\n\nndata {_data}\n\n\n\n\n")
        g_user_id = 0

        if len(_data) == 0:
            await event.respond(f'Изображение с нумерацией "{image_num}" никто не скачал')
            del admin_state[who]

            return
        
        g_user_id = _data[0][0]
        req_user = await client.get_entity(g_user_id)

        g_user_name = req_user.username
        g_user_id = req_user.id
        g_user_firstname = req_user.first_name
        g_user_last_name = ''
        if req_user.last_name != None: g_user_last_name = req_user.last_name

        user_info = f"Информация о пользователе получившем изображение:\n"
        user_info = user_info + f"Имя аккаунта пользователя: @{g_user_name}\n"
        user_info = user_info + f"ID пользователя: {g_user_id}\n"
        user_info = user_info + f"Полнок имя аккаунта: {g_user_firstname} {g_user_last_name}"

        await event.respond(f'{user_info}')

        del admin_state[who]

#IMAGE EDITING
    elif state == EditPhotoPackState.IMAGE_NEW_NAME:
        selected_image_name = admin_state_memory[f"{who}_nn"]
        new_name = event.raw_text
        print(selected_image_name)
        cur.execute(f"UPDATE image_list SET picture_name='{new_name}' WHERE picture_name='{selected_image_name}'")
        con.commit()
        await client.send_message(who,f"Теперь новое имя для {selected_image_name}: {new_name}.")
        del admin_state[who]

    elif state == EditPhotoPackState.IMAGE_WATERMARK_SETTINNG:
        selected_image_name = admin_state_memory[f"{who}_nn"]
        print(selected_image_name)
        new_params = event.raw_text
        cur.execute(f"UPDATE image_list SET image_watermark_params='{new_params}' WHERE picture_name='{selected_image_name}'")
        con.commit()
        await create_and_send_photo_with_watermark(user_id=who, image_name=selected_image_name, msg_id=0, t_text='0', mode=3)
        await client.send_message(who,f"Теперь новsе параметры для {selected_image_name}: {new_params}.")
        del admin_state[who]


@client.on(events.NewMessage(pattern='/pacsess', chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = admin_state.get(who)
    print(f'Admin state for {who}: {state}')
    if state is None:
        cur.execute("SELECT * FROM image_list")
        _data = cur.fetchall()
        if len(_data) == 0:
            await client.send_message(who,"В базе данных нет фото")
            return
        
        _buttons = []
        for row in _data:
            name = row[1]
            name_id = f"{name}_i_s_ac_a_b".encode("utf-8")
            # print(f"Btn {row[1]}: {name_id}")
            _buttons.append(Button.inline(name, bytes(name_id)))
        _buttons = await convert_1d_to_2d(_buttons, 3)

        await client.send_message(who,"Выберите фото для изменения доступа", buttons= _buttons)
        
        admin_state[who] = SetImageAccessState.SELECT_IMAGE


#ADMIN ID KEYBOARD
@client.on(events.CallbackQuery(chats=BOT_ADMIN_ID))
async def admin_cms_callback(event):
    who = event.sender_id
    # if who in BOT_ADMIN_ID:
    state = admin_state.get(who)
    print(f'Admin state for {who}: {state}')
    #SELECT IMAGE TO VIEW USER
    if state == GetUserByPhonoNumberState.SELECT_IMAGE:
        edata_d = event.data.decode('utf-8')
        admin_state_memory[f'get_image_name_state_{who}'] = edata_d.replace("_get_user_by_image_admin_btn", '')
        await client.send_message(who,f"Вы выбрали {admin_state_memory[f'get_image_name_state_{who}']}")
        await client.send_message(who,"Введите число на фото.")

        admin_state[who] = GetUserByPhonoNumberState.SELECT_NUMBER_ON_PICTURE

    #SELECT IMAGE TO CHANGE ACCSESS
    elif state == SetImageAccessState.SELECT_IMAGE:
        edata_d = event.data.decode('utf-8')

        selected_image_name = edata_d.replace("_i_s_ac_a_b", '')
        cur.execute("SELECT picture_access FROM image_list WHERE picture_name=?", (selected_image_name,))
        _data = cur.fetchall()
        if len(_data) == 0:
            await client.send_message(who,"В базе данных нет фото")
            return
        
        button = []

        btn_enable = f"{who}_{selected_image_name}_i_all_ac_admin_btn".encode("utf-8") 
        btn_disable = f"{who}_{selected_image_name}_i_dis_ac_admin_btn".encode("utf-8") 
        if _data[0][0] == 'True':
            button.append(Button.inline("Закрыть доступ", bytes(btn_disable)))

        elif _data[0][0] == 'False':
            button.append(Button.inline("Открыть доступ", bytes(btn_enable)))

        await client.send_message(who,f"Установите доступ для {selected_image_name}.", buttons=button)

        admin_state[who] = SetImageAccessState.SET_IMAGE_ACCESS
    
    elif state == SetImageAccessState.SET_IMAGE_ACCESS:
        edata_d = event.data.decode('utf-8')
        selected_image_name = ''

        reply = ['Фото в открытом доступе', 'Фото в закрытом доступе']
        msg = ''
        access = ''
        if ("_i_all_ac_admin_btn" in edata_d) and (str(who) in edata_d):
            selected_image_name = edata_d.replace("_i_all_ac_admin_btn", '').replace(f"{who}_", '')
            access = 'True'
            msg = reply[0]

        elif ("_i_dis_ac_admin_btn" in edata_d) and (str(who) in edata_d):
            selected_image_name = edata_d.replace("_i_dis_ac_admin_btn", '').replace(f"{who}_", '')
            access = 'False'
            msg = reply[1]
        cur.execute(f"UPDATE image_list SET picture_access='{access}' WHERE picture_name='{selected_image_name}'")
        con.commit()

        await client.send_message(who, msg)
        del admin_state[who]
    
    # SELECT IMAGE TO DELETE
    elif state == CreateDeletePhotoPackState.SELECT_IMAGE_TO_DELETE:
        edata_d = event.data.decode('utf-8')
        selected_image_name = edata_d.replace(f"_{who}_gi_del_a_b", '')

        button = []
        btn_confirm = f"{selected_image_name}_i_yes_del_adm_btn".encode("utf-8") 
        btn_discard = f"{selected_image_name}_i_no_de_adm_btn".encode("utf-8")

        button.append(Button.inline("Подтвердить удаление", bytes(btn_confirm)))
        button.append(Button.inline("Отменить удаление", bytes(btn_discard)))

        admin_state[who] = CreateDeletePhotoPackState.CONFIRM_DELETING_SELECTED_IMAGE
        await client.send_message(who,f"Подтвердите или отклоние удаление {selected_image_name}.", buttons=button)


    elif state == CreateDeletePhotoPackState.CONFIRM_DELETING_SELECTED_IMAGE:
        edata_d = event.data.decode('utf-8')
        selected_image_name = ''
        if f'_i_yes_del_adm_btn' in edata_d:
            selected_image_name = edata_d.replace(f"_i_yes_del_adm_btn", '')
            cur.execute("SELECT picture_path FROM image_list WHERE picture_name=?", (selected_image_name,))
            _data = cur.fetchall()
            path = _data[0][0]

            cur.execute("DELETE FROM image_list WHERE picture_name=?", (selected_image_name,))
            cur.execute("DELETE FROM bot_library WHERE picture_name=?", (selected_image_name,))
            con.commit()
            os.remove(path)
            await client.send_message(who, f"Фото {selected_image_name} удалено.")

        elif f'_i_no_de_adm_btn' in edata_d:
            selected_image_name = edata_d.replace('_i_no_de_adm_btn','')
            await client.send_message(who, f"Фото {selected_image_name} сохранено.")

        del admin_state[who]

    

    # SELECT IMAGE TO EDIT
    elif state == EditPhotoPackState.SELECT_IMAGE:
        edata_d = event.data.decode('utf-8')
        selected_image_name = edata_d.replace(f"_{who}_gi_edi_a_b", '')

        button = []
        btn_name = f"{selected_image_name}_EdiNameAdmBtn".encode("utf-8") 
        btn_params = f"{selected_image_name}_EdiParamsAdmBtn".encode("utf-8")

        button.append(Button.inline("Изменить имя изображения", bytes(btn_name)))
        button.append(Button.inline("Изменить параметры ватермарки на изображении", bytes(btn_params)))

        admin_state[who] = EditPhotoPackState.SELECT_OPTION
        await client.send_message(who,f"Выберите дейстивие для {selected_image_name}.", buttons=button)
        

# SELECT IMAGE TO EDIT KEYBOARD QUERY
@client.on(events.CallbackQuery(chats=BOT_ADMIN_ID))
async def edit_image_action(event):
    who = event.sender_id
    state = admin_state.get(who)
    print(f'Admin state for {who}: {state}')
    if state == EditPhotoPackState.SELECT_OPTION:
        edata_d = event.data.decode('utf-8')
        print(edata_d)
        if '_EdiNameAdmBtn' in edata_d:
            print('_EdiNameAdmBtn')
            name = edata_d.replace(f"_EdiNameAdmBtn", '')
            await client.send_message(who,f"Введите новое имя {name}.")
            admin_state_memory[f"{who}_nn"] = name
            print(admin_state_memory[f"{who}_nn"])
            admin_state[who] = EditPhotoPackState.IMAGE_NEW_NAME

        elif '_EdiParamsAdmBtn' in edata_d:
            msg = """
Хорошо! Ведите параметры расположения и цвета ватермарки.
x y/hex/a/scale
x, y - звдиг по пикселям от верхнего левого угла.
hex - цвет в hex.
a - прозрачность текста (0-100).
scale - размер текста (0, 1, 2, ...).
Пример: 100 20/00ff00/70/50
"""
            name = edata_d.replace(f"_EdiParamsAdmBtn", '')
            await client.send_message(who,f"Введите новые параметры ватермарки для {name}.")
            await client.send_message(who,msg)
            admin_state_memory[f"{who}_nn"] = name
            admin_state[who] = EditPhotoPackState.IMAGE_WATERMARK_SETTINNG



@client.on(events.CallbackQuery(data='admin_cancel_action'))
async def admin_cancel_action(event):
    who = event.sender_id
    del admin_state[who]
    print(f'Admin state for {who}: {admin_state[who]}')


@client.on(events.NewMessage(pattern='/editphoto', chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = admin_state.get(who)
    print(f'Admin state for {who}: {state}')


    cur.execute("SELECT * FROM image_list")
    _data = cur.fetchall()
    
    _buttons = []
    if len(_data) == 0:
        await client.send_message(who,"В базе данных нет фото")
        return

    for row in _data:
        name = row[1]
        name_id = f"{name}_{who}_gi_edi_a_b".encode("utf-8")
        _buttons.append(Button.inline(name, bytes(name_id)))

    _buttons = await convert_1d_to_2d(_buttons, 2)

    await client.send_message(who,"Выберите изображение для редактирования:", buttons = _buttons)

    admin_state[who] = EditPhotoPackState.SELECT_IMAGE
