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


#ADMIN CMS FSM
class CreateDeletePhotoPackState(Enum):
    SEND_IMAGE = auto()
    IMAGE_NEW_NAME = auto()
    IMAGE_WATERMARK_SETTINNG = auto()
    IMAGES_COUNT = auto()

    START_DELETING_IMAGE = auto()
    SELECT_IMAGE_TO_DELETE = auto()
    CONFIRM_DELETING_SELECTED_IMAGE = auto()

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
    msg = '/createphoto\n'
    msg = msg + '/deletephoto\n' 
    msg = msg + '/pacsess\n'
    msg = msg + '/getuserbyphoto\n'
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
        msg = 'Хорошо! Ведите параметры расположения и цвета ватермарки.\n'
        msg = msg + 'x y/hex/a/scale\n'
        msg = msg + 'x, y - звдиг по пикселям от верхнего левого угла.\n'
        msg = msg + 'hex - цвет в hex.\n'
        msg = msg + 'a - прозрачность текста (0-100).\n'
        msg = msg + 'scale - размер текста (0, 1, 2, ...).\n'
        msg = msg + 'Пример: 100 20/00ff00/70/50\n'
        
        await event.respond(msg)
        admin_state[who] = CreateDeletePhotoPackState.IMAGE_NEW_NAME

    elif state == CreateDeletePhotoPackState.IMAGE_NEW_NAME:

        path = admin_state_memory[f'inp_path_{who}']
        image_new_name = admin_state_memory[f'image_new_name_{who}']
        params =  event.text

        res = (await save_photo_to_lib(who, image_new_name, params, path))
        await client.send_message(who, "Изображение успешно добавлено")
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
        photo_fullname = f"{photo_name}_{image_num}"
        # photopath = f"{SAVE_FOLDER}{photo_name}/"
        # for fn in Path(photopath).glob(f'{photo_fullname}.*'):
        #     photopath = fn

        # await client.send_file(who, file=f'{photopath}', force_document=True)

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


@client.on(events.NewMessage(pattern='/pacsess', chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = admin_state.get(who)

    if state is None:
        cur.execute("SELECT * FROM image_list")
        _data = cur.fetchall()
        if len(_data) == 0:
            await client.send_message(who,"В базе данных нет фото")
            return
        
        _buttons = []
        for row in _data:
            name = row[1]
            name_id = f"{name}_image_to_set_accsess_admin_btn".encode("utf-8")
            _buttons.append(Button.inline(name, bytes(name_id)))
        _buttons = await convert_1d_to_2d(_buttons, 3)

        await client.send_message(who,"Выберите фото для изменения доступа", buttons= _buttons)
        
        admin_state[who] = SetImageAccessState.SELECT_IMAGE


#ADMIN ID KEYBOARD
@client.on(events.CallbackQuery())
async def admin_cms_callback(event):
    who = event.sender_id
    if who in BOT_ADMIN_ID:
        state = admin_state.get(who)

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

            selected_image_name = edata_d.replace("_image_to_set_accsess_admin_btn", '')
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
                # photopath = f"{SAVE_FOLDER}{selected_image_name}"
                # shutil.rmtree(photopath)
                cur.execute("DELETE FROM image_list WHERE picture_name=?", (selected_image_name,))
                cur.execute("DELETE FROM bot_library WHERE picture_name=?", (selected_image_name,))
                con.commit()
                await client.send_message(who, f"Фото {selected_image_name} удалено.")

            elif f'_i_no_de_adm_btn' in edata_d:
                selected_image_name = edata_d.replace('_i_no_de_adm_btn','')
                await client.send_message(who, f"Фото {selected_image_name} сохранено.")

            del admin_state[who]

@client.on(events.CallbackQuery(data='admin_cancel_action'))
async def admin_cancel_action(event):
    who = event.sender_id
    del admin_state[who]

async def Create_PhotoPack(photo_dir, new_name, counts, params):
    params = params.split('/')
    t_pos = params[0].split(' ')
    t_hex = params[1].split(' ')
    t_hex = str(t_hex[0])

    t_opacity = int(params[2])
    t_scale = int(params[3])

    rgb = tuple(int(t_hex[i:i+2], 16) for i in (0, 2, 4))

    x = int(t_pos[0])
    y = int(t_pos[1])

    a = int((t_opacity*255)/100)
    try:
        title_font = ImageFont.truetype('fonts/PlayfairDisplay-Medium.ttf', t_scale)
        path = os.path.join(SAVE_FOLDER, new_name)
        try:
            os.mkdir(str(path)) 
        except OSError as error:
            if error == 'Cannot create a file when that file already exists:':
                path = path
        

        cur.execute("SELECT * FROM image_list WHERE picture_name=?", (new_name,))
        _data=cur.fetchall()
        if len(_data) != 0:
            return 2

        cur.execute(f"INSERT INTO image_list VALUES ('{new_name}', 'False')")
        con.commit()

        for i in range(0, int(counts)):
            userid = None
            full_name = f"{new_name}_{i}"
            userid = 0
            my_image = Image.open(photo_dir)
            format = my_image.format
            my_image = my_image.convert("RGBA")
            title_text = i

            txt = Image.new("RGBA", my_image.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt)
            d.text((x, y), str(title_text), font=title_font, fill=(rgb[0], rgb[1], rgb[2], a))

            my_image = Image.alpha_composite(my_image, txt).convert("RGB")

            my_image.save(f"{path}/{new_name}_{i}.png", "PNG")

            # my_image.save(f"{path}/{new_name}_{i}.{format}")
            my_image.close()

            cur.execute(f"INSERT INTO bot_library VALUES ({userid}, '{new_name}', {i}, '{full_name}')")
            con.commit()
            print(f"Image {full_name} - created. ")
        return 0

    except Exception as e:
        print(e)
        return 1