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
    await client.send_message(event.sender_id, "msg", buttons=buttons)


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
        if row[1] == 'True':
            name = row[0]
            name_id = f"{name}_{sender_id}gi_usr_btn".encode("utf-8")
            _buttons.append(Button.inline(name, bytes(name_id)))

    _buttons = await convert_1d_to_2d(_buttons, 3)

    await client.edit_message(sender_id, event.message_id,"Выберите фото", buttons = _buttons)


@client.on(events.CallbackQuery())
async def user_image_callback(event):
    sender_id = event.sender_id
    edata_d = event.data.decode('utf-8')
    if f'_{sender_id}gi_usr_btn' in edata_d:
        clear_data = edata_d.replace(f"_{sender_id}gi_usr_btn", '')
        cur.execute("SELECT * FROM image_list")
        _data = cur.fetchall()
        for row in _data:
            if row[1] == 'True':
                name = row[0]
                if name == clear_data:
                    await send_nudes(sender_id, name)
                    break
        await client.delete_messages(sender_id, event.message_id)

