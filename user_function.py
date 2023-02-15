from pathlib import Path
from function import *
from database_manager import *
import random
from PIL import Image, ImageFont, ImageDraw 
import os

from pathlib import Path

from telethon import functions

async def check_user(user_id):
    # user_id = str(user_id)
    # ent = await client.get_entity(user_id)
    # print(str(ent))
    active_users = client.iter_participants(channel_id, aggressive=True, limit=3000)
    print(active_users)
    async for i in active_users:
        print(i)
        if int(user_id) == int(i.id):
            return True
    else: return False




async def create_and_send_photo_with_watermark(user_id, image_name, msg_id, t_text, mode):
    print('Creating new image')
    cur.execute("SELECT * FROM image_list WHERE picture_name=?", (image_name,))
    _data=cur.fetchall()
    if len(_data) == 0:
        return f"There's not image with name {image_name}"
    print(_data)
    params = _data[0][3]
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
    print(_data[0][4])
    inp_photo_dir =  _data[0][4]
    my_image = Image.open(inp_photo_dir)
    format = my_image.format
    my_image = my_image.convert("RGBA")

    new_name = random.randint(26571, 26457454)

    txt = Image.new("RGBA", my_image.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    d.text((x, y), str(t_text), font=title_font, fill=(rgb[0], rgb[1], rgb[2], a))

    my_image = Image.alpha_composite(my_image, txt).convert("RGB")

    send_path = f"{SAVE_FOLDER}{new_name}.png"
    print(send_path)
    # my_image.quantize(colors=1024, method=Image.MAXCOVERAGE)
    my_image.save(send_path) #"PNG",
    my_image.close()
    await client.send_file(user_id, file=send_path, force_document=True)

    t_text = int(t_text)

    if mode == 0:  
        cur.execute(f"INSERT INTO bot_library VALUES ({user_id}, '{image_name}', {msg_id}, {t_text})")
        con.commit()
        print(f"Image '{new_name}' - saved. ")

    if mode == 1:  
        cur.execute(f"UPDATE bot_library SET picture_msg_id='{msg_id}' WHERE picture_name='{image_name}' AND user_id='{user_id}'")
        con.commit()
        print(f"Image '{new_name}' - saved. ")
    if mode == 3:
        print(f"Test image '{new_name}' has been sended. ")
        return
    

    os.remove(send_path)


# optimize=True