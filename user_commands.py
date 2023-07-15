from database_manager import *
from function import *
from user_function import *
from telethon.tl.custom import Button
from user_keyboard import *
@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    sender_id = event.sender_id
    user_menu_state[sender_id] = 0

    if await check_user(sender_id) == False:
        await client.send_message(sender_id,"У вас нет подписки")
        return

    cur.execute('SELECT user_id FROM user_list WHERE user_id = ?', (sender_id,))
    _data=cur.fetchall()

    if len(_data) == 0:
        cur.execute(f"INSERT INTO user_list VALUES ({sender_id}, 'True')")
        con.commit()
        print("NONO")
    buttons = []
    buttons.append(Button.inline('Получить фото', 'get_photos'))
    await client.send_message(event.sender_id, 'Привет! Я могу выдать тебе 4к картинки из канала legionCumMander. Для того, чтобы начать нажми "Получить фото"', buttons=buttons)



@client.on(events.CallbackQuery(data='get_photos'))
async def user_get_image(event):
    who = event.sender_id

    if await check_user(who) == False:
        await client.send_message(who,"У вас нет подписки")
        await event.answer("У вас нет подписки")
        return

    cur.execute("SELECT * FROM image_list ORDER BY rowid DESC")
    _data = cur.fetchall()
    if len(_data) == 0:
        await client.send_message(who,"В базе данных нет фото")
        return
    
    user_full_menu_list[who] = _data
    user_full_menu_list[f"{who} revnum="] = True
    user_full_menu_list[f"{who} revname="] = False
    _data.sort(reverse=True, key=get_date)
    print("Menu list updated")
    await usr_load_5_pic(event)
    


@client.on(events.CallbackQuery())
async def user_image_callback(event):
    who = event.sender_id
    edata_d = event.data.decode('utf-8')
    
    if f'_{who}gi_usr_btn' in edata_d:
        _picture_name = edata_d.replace(f"_{who}gi_usr_btn", '')  

        cur.execute("SELECT * FROM user_list WHERE user_id=?", (who,))
        _data=cur.fetchall()
        print(_data)
        if _data[0][1] == 'False': 
            return "User not allowed"

        print(f"Request for image: {_picture_name} , by {who}")
        cur.execute("SELECT * FROM bot_library WHERE user_id=? AND picture_name=?", (who, _picture_name,))
        _data=cur.fetchall()

        if len(_data) == 0:
            print('Image for user is not created')
            cur.execute("SELECT * FROM bot_library WHERE picture_name=?", (_picture_name,))
            msg_data=cur.fetchall()
            picid = len(msg_data) + 1
            msg_id = event.message_id + 1
            await create_and_send_photo_with_watermark(who, _picture_name, msg_id, picid, 0)
            # await client.edit_message(who, event.message_id,"Изображение загружается", buttons = None)
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


