import json
import os

import requests
import misc
import datetime
import random
import telebot
from bs4 import BeautifulSoup

token = misc.token
URL = 'https://api.telegram.org/bot' + token + '/'
URL_CHAT = 'https://forum.originalpw.com/topic/3484-чатик-20/'
global last_update_id
last_update_id = 0
bot = telebot.TeleBot(token)


def get_all_photo():
    path = 'image/'
    lst = os.listdir(path)
    all_name_photo = {}
    for l in lst:
        all_name_photo[l] = l
    return all_name_photo


def get_update():
    global last_update_id
    updates = bot.get_updates(offset=last_update_id + 100, timeout=500)
    return updates


def get_message():
    data = get_update()
    photo = None
    text_message = None
    photo_name = None
    last_update = data[-1].update_id
    chat_id = data[-1].message.chat.id
    is_photo = False
    if data[-1].message.text is not None:
        text_message = data[-1].message.text
    if data[-1].message.photo is not None:
        photo = data[-1].message.photo
        is_photo = True
    message_id = data[-1].message.id
    if data[-1].message.caption is not None:
        photo_name = data[-1].message.caption
    message = {'chat_id': chat_id,
               'text_message': text_message,
               'last_update_id': last_update,
               'photo': photo,
               'is_photo': is_photo,
               'photo_name': photo_name,
               'message_id': message_id}

    return message


def send_message(chat_id, text_message):
    bot.send_message(chat_id, text_message)


def send_all_photo_name(chat_id, all_photo):
    string = "Пожалуйста, введите одно из этих названий без .png :\n\n"
    index = 0
    for i in all_photo:
        string += str(index + 1) + '. ' + i + '\n'
        index += 1

    send_message(chat_id, string)


def save_photo(photo, name):
    file_info = bot.get_file(photo[len(photo) - 1].file_id)
    all_photo = get_all_photo()
    if name is not None:
        file_name_key = name
    else:
        i = 1
        file_name_key = str(i) + '.png'
        while file_name_key in all_photo:
            i += 1
            file_name_key = str(i) + '.png'
    downloaded_file = bot.download_file(file_info.file_path)

    path = 'image/' + file_name_key
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)


def send_photo(chat_id):
    all_photo = os.listdir('image')
    if len(all_photo) == 0:
        send_message(chat_id, "Добавьте фотографии, пока что пусто")
    else:
        file = random.choice(all_photo)
        photo = open('image/' + file, 'rb')
        bot.send_photo(chat_id, photo=photo)


def send_photo_name(chat_id, name):
    all_photo = get_all_photo()
    photo = open('image/' + all_photo[name], 'rb')
    bot.send_photo(chat_id, photo=photo)


def current_time():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M")


def get_soup_by_url(cur_url):
    page = requests.get(cur_url)
    soup = BeautifulSoup(page.text, 'xml')
    return soup


def get_last_message_on_chat():
    soup = get_soup_by_url(URL_CHAT)
    li = soup.find(class_='ipsPagination_last')
    soup = get_soup_by_url(li.find('a').get('href'))
    s = soup.find_all('h3', class_='ipsType_sectionHead cAuthorPane_author ipsType_blendLinks ipsType_break')
    name_block = s[-1].text
    pos = name_block.split(" ")
    name = ""
    for i in range(len(pos)):
        if pos[i - 1] == "профиль":
            name = pos[i][0:-1]
    s = soup.find_all('p')
    text = s[-23].text[1:]
    return {'user_name': name,
            'text_message': text}


def delete_all_photo():
    path = 'image/'
    all_photo = get_all_photo()
    for photo in all_photo:
        os.remove(path + photo)


def main():
    while True:
        message = get_message()
        global last_update_id
        if last_update_id == 0:
            last_update_id = message['last_update_id']
        elif last_update_id != message['last_update_id']:
            chat_id = message['chat_id']
            text_message = message['text_message']
            text = ''
            if text_message == '/help':
                text = "Вот что я умею:\n" \
                       "1. /help - список всех команд.\n" \
                       "2. /time - Отправить текущее дата время.\n" \
                       "3. /last - Последнее сообщение с Чатик 2.0 \n" \
                       "4. /photo - Отправить случайное фото.\n" \
                       "5. Отправь фото и оно сохранится для рандомного отправления.\n" \
                       "6. /delete_photo - удалить все фотографии. \n" \
                       "7. /send_photo {name} - отправить фотографию с названием name. Если нет параметра name, то" \
                       " будет предложено выбрать из списка только название"
            elif text_message == '/time':
                text = current_time()
            elif text_message == '/last':
                temp = get_last_message_on_chat()
                text = f'{temp["user_name"]} : {temp["text_message"]}'
            elif text_message == '/photo':
                send_photo(chat_id)
                text = None
            elif message['is_photo']:
                all_photo = get_all_photo()
                photo = message['photo']
                photo_name = None
                if message['photo_name'] is not None:
                    photo_name = message['photo_name'] + '.png'
                    while photo_name in all_photo:
                        message = get_message()
                        if message['text_message'] is not None:
                            photo_name = get_message()['text_message'] + '.png'
                        if last_update_id != message['last_update_id']:
                            if photo_name in all_photo:
                                send_message(chat_id, "Пожалуйста, введите другое имя для фотографии.")
                            last_update_id = message['last_update_id']
                            if message['text_message'] is not None:
                                photo_name = get_message()['text_message'] + '.png'
                        last_update_id = message['last_update_id']
                last_update_id = message['last_update_id']
                save_photo(photo, photo_name)
                text = "Фотография успешно добавлена"
            elif text_message == '/delete_photo':
                delete_all_photo()
                text = "Все фотографии удалены"
            elif text_message.find('/send_photo') != -1:
                all_photo = get_all_photo()
                if len(all_photo) == 0:
                    text = "Нет фотографий"
                else:
                    photo_name = text_message[12:] + '.png'
                    while not (photo_name in all_photo):
                        message = get_message()
                        if message['text_message'] is not None:
                            photo_name = get_message()['text_message'] + '.png'
                        if last_update_id != message['last_update_id']:
                            if not (photo_name in all_photo):
                                send_all_photo_name(chat_id, all_photo)
                            last_update_id = message['last_update_id']
                            if message['text_message'] is not None:
                                photo_name = get_message()['text_message'] + '.png'
                        last_update_id = message['last_update_id']
                    send_photo_name(chat_id, photo_name)
                    text = None
                last_update_id = message['last_update_id']
            else:
                text = "Я не знаю такой команды"
            if text is not None:
                send_message(chat_id, text)
            last_update_id = message['last_update_id']


if __name__ == '__main__':
    main()
    bot.polling()
