from database_manager import *
from function import *
from user_function import *
from telethon.tl.custom import Button


@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    sender_id = int(event.sender_id)
    cur.execute('SELECT user_id FROM user_list WHERE user_id = ?', (sender_id,))
    _data=cur.fetchall()

    if len(_data) == 0:
        cur.execute(f"INSERT INTO user_list VALUES ({sender_id}, 'True')")
        con.commit()
    buttons = []
    buttons.append(Button.inline('Получить фото', 'get_photos'))
    await client.send_message(event.sender_id, 'Привет! Я могу выдать тебе 4к картинки из канала legionCumMander. Для того, чтобы начать нажми "start"', buttons=buttons)


@client.on(events.CallbackQuery(data='get_photos'))
async def user_get_image(event):
    sender_id = event.sender_id
    cur.execute("SELECT * FROM image_list")
    _data = cur.fetchall()

    _buttons = []

    if len(_data) == 0:
        await client.send_message(sender_id,"В базе данных нет фото")
        return

    for row in _data:
        if row[2] == 'True':
            name = row[1]
            name_id = f"{name}_{sender_id}gi_usr_btn".encode("utf-8")
            _buttons.append(Button.inline(name, bytes(name_id)))

    if len(_buttons) == 0:
        _buttons = await convert_1d_to_2d(_buttons, 3)
        await client.edit_message(sender_id, event.message_id, "В базе данных нет доступных фото.")
        return

    await client.edit_message(sender_id, event.message_id,"Выберите фото", buttons = _buttons)


@client.on(events.CallbackQuery())
async def user_image_callback(event):
    # sender_id = event.sender_id
    who = event.sender_id

    

    edata_d = event.data.decode('utf-8')
    _picture_name = ''
    if f'_{who}gi_usr_btn' in edata_d:
        _picture_name = edata_d.replace(f"_{who}gi_usr_btn", '')
        

    cur.execute("SELECT * FROM user_list WHERE user_id=?", (who,))
    _data=cur.fetchall()
    print(_data)
    if _data[0][1] == 'False': 
        return "User not allowed"


    cur.execute("SELECT * FROM bot_library WHERE user_id=? AND picture_name=?", (who, _picture_name,))
    _data=cur.fetchall()

    if len(_data) == 0:
        print('Image for user is not created')
        cur.execute("SELECT * FROM bot_library WHERE picture_name=?", (_picture_name,))
        msg_data=cur.fetchall()
        picid = len(msg_data) + 1
        msg_id = event.message_id + 1
        await client.edit_message(who, event.message_id,"Изображение загружается", buttons = None)
        await create_and_send_photo_with_watermark(who, _picture_name, msg_id, picid, 0)
        return
    


    msg_id = event.message_id + 1
    picid = _data[0][3]
    await create_and_send_photo_with_watermark(who, _picture_name, msg_id, picid, 1)
    # try:
    #     msgid = _data[0][2]
    #     await client.forward_messages(who, msgid, from_peer=who)
    # except:
    #     msg_id = event.message_id + 1
    #     picid = _data[0][3]
    #     await create_and_send_photo_with_watermark(who, _picture_name, msg_id, picid, 1)


