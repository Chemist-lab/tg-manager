from enum import Enum, auto
import os
from config import *
from function import *
from database_manager import *

from telethon import events
from telethon.tl.custom import Button


from PIL import Image, ImageFont, ImageDraw 
import random


class TestCreateDeletePhotoPackState(Enum):
    SEND_IMAGE = auto()
    IMAGE_NEW_NAME = auto()
    IMAGE_WATERMARK_SETTINNG = auto()

    START_DELETING_IMAGE = auto()
    SELECT_IMAGE_TO_DELETE = auto()
    CONFIRM_DELETING_SELECTED_IMAGE = auto()

# The state in which different users are, {user_id: state}
test_admin_state = {}

test_admin_state_memory = {}

# UPLOAD NEW IMAGE
@client.on(events.NewMessage(chats=BOT_ADMIN_ID))
async def admin_cms(event):
    who = event.sender_id
    state = test_admin_state.get(who)   

    if event.raw_text == '/testcreatephoto':
        if state is None:
            await event.respond('Отправьте фото')
            test_admin_state[who] = TestCreateDeletePhotoPackState.SEND_IMAGE

    elif state == TestCreateDeletePhotoPackState.SEND_IMAGE:
        test_admin_state_memory[f'inp_path_{who}'] = str(await event.download_media(TG_SAVE_PATH))
        await event.respond('Хорошо! Задайте имя фото:')
        test_admin_state[who] = TestCreateDeletePhotoPackState.IMAGE_WATERMARK_SETTINNG

    elif state == TestCreateDeletePhotoPackState.IMAGE_WATERMARK_SETTINNG:
        wrong = ['/', '"\"']
        for wr in wrong:
            if wr in event.text:
                await event.respond('Недопустимые символы в названии!\nПопробуйте ещё раз:')
                state == TestCreateDeletePhotoPackState.SEND_IMAGE
                return
        
        test_admin_state_memory[f'image_new_name_{who}'] = event.text
        msg = 'Хорошо! Ведите параметры расположения и цвета ватермарки.\n'
        msg = msg + 'x y/hex/a/scale\n'
        msg = msg + 'x, y - звдиг по пикселям от верхнего левого угла.\n'
        msg = msg + 'hex - цвет в hex.\n'
        msg = msg + 'a - прозрачность текста (0-100).\n'
        msg = msg + 'scale - размер текста (0, 1, 2, ...).\n'
        msg = msg + 'Пример: 100 20/00ff00/70/50\n'
        
        await event.respond(msg)
        test_admin_state[who] = TestCreateDeletePhotoPackState.IMAGE_NEW_NAME

    elif state == TestCreateDeletePhotoPackState.IMAGE_NEW_NAME:

        path = test_admin_state_memory[f'inp_path_{who}']
        image_new_name = test_admin_state_memory[f'image_new_name_{who}']
        params =  event.text

        res = (await save_photo_to_lib(who, image_new_name, params, path))

        del test_admin_state[who]
        del test_admin_state_memory[f'inp_path_{who}']
        del test_admin_state_memory[f'image_new_name_{who}']



async def save_photo_to_lib(_user_id, _picture_name, _params, _image_path):
    cur.execute("SELECT * FROM image_list WHERE picture_name=?", (_picture_name,))
    _data=cur.fetchall()
    if len(_data) != 0:
        return 2
    cur.execute(f"INSERT INTO image_list VALUES ('{_user_id}', '{_picture_name}', 'False', '{_params}', '{_image_path}')")
    con.commit()
    return 0




# @client.on(events.NewMessage(pattern='/deletephoto', chats=BOT_ADMIN_ID))
# async def admin_cms(event):
#     who = event.sender_id
#     cur.execute("SELECT * FROM image_list")
#     _data = cur.fetchall()

#     _buttons = []
#     if len(_data) == 0:
#         await client.send_message(who,"В базе данных нет фото")
#         return

#     for row in _data:
#         name = row[0]
#         name_id = f"{name}_{who}_gi_del_a_b".encode("utf-8")
#         _buttons.append(Button.inline(name, bytes(name_id)))

#     _buttons = await convert_1d_to_2d(_buttons, 2)

#     await client.send_message(who,"Выберите фото пак для удаления:", buttons = _buttons)

#     test_admin_state[who] = TestCreateDeletePhotoPackState.SELECT_IMAGE_TO_DELETE

# , chats=BOT_ADMIN_ID
@client.on(events.NewMessage(pattern='/testsend'))
async def admin_command(event):
    who = event.sender_id
    _picture_name = 'legs'
    cur.execute("SELECT * FROM user_list WHERE user_id=?", (who,))
    _data=cur.fetchall()
    print(_data)
    if _data[0][1] == 'False': 
        return "User not allowed"


    cur.execute("SELECT * FROM bot_library WHERE user_id=? AND picture_name=?", (who, _picture_name,))
    _data=cur.fetchall()

    cur.execute("SELECT * FROM bot_library WHERE picture_name=?", (_picture_name,))
    msg_data=cur.fetchall()


    if len(_data) == 0:
        print('Image for user is not created')
        msg_id = event.id + 1
        await create_and_send_photo_with_watermark(who, _picture_name, msg_id)
        return

    
    try:
        msgid = _data[0][2]
        await client.forward_messages(who, msgid, from_peer=who)
    except:
        msg_data
    



# async def send_photo_with_watermark(user_id, image_name, params):
#     await client.forward_messages(user_id, file='sad', force_document=True)
        

async def create_and_send_photo_with_watermark(user_id, image_name, msg_id, t_text):
    print('Creating new image')
    cur.execute("SELECT * FROM image_list WHERE picture_name=?", (image_name,))
    _data=cur.fetchall()
    if len(_data) == 0:
        return f"There's not image with name {image_name}"
    print(_data)

    params = _data[0][3]
    print(params)

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
    title_font = ImageFont.truetype('fonts/PlayfairDisplay-Medium.ttf', t_scale)
    inp_photo_dir = os.path.join(TG_SAVE_PATH, 'test.png')
    my_image = Image.open(inp_photo_dir)

    format = my_image.format

    my_image = my_image.convert("RGBA")
    

    new_name = random.randint(26571, 26457454)


    # cur.execute("SELECT * FROM bot_library WHERE picture_name=?", (image_name,))
    # _data=cur.fetchall()
    # i = len(_data) + 1
    # title_text = str(i)

    txt = Image.new("RGBA", my_image.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    d.text((x, y), str(t_text), font=title_font, fill=(rgb[0], rgb[1], rgb[2], a))

    my_image = Image.alpha_composite(my_image, txt).convert("RGB")

    send_path = f"{SAVE_FOLDER}{new_name}.png"
    print(send_path)
    my_image.save(send_path, "PNG")

    my_image.close()
    await client.send_file(user_id, file=send_path, force_document=True)

    t_text = int(t_text)

    cur.execute(f"INSERT INTO bot_library VALUES ({user_id}, '{image_name}', {msg_id}, {t_text})")
    con.commit()
    print(f"Image {new_name} - saved. ")
    os.remove(send_path)