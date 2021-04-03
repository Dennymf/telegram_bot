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


def get_update():
    url = URL + 'getupdates'
    r = requests.get(url)
    return r.json()


def get_message():
    data = get_update()
    object = data['result'][-1]
    photo = None
    text_message = None
    last_update = object['update_id']
    chat_id = object['message']['chat']['id']
    is_photo = False
    if object['message'].get('text') is not None:
        text_message = object['message']['text']
    if object['message'].get('photo') is not None:
        photo = object['message']['photo']
        is_photo = True
    message = {'chat_id': chat_id,
               'text_message': text_message,
               'last_update_id': last_update,
               'photo': photo,
               'is_photo': is_photo}

    return message


def send_message(chat_id, text_message):
    url = URL + f'sendmessage?chat_id={chat_id}&text={text_message}'
    requests.get(url)


def save_photo(photo):
    file_info = bot.get_file(photo[len(photo) - 1]['file_id'])
    downloaded_file = bot.download_file(file_info.file_path)
    path = 'image/' + photo[1]['file_id']
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
    all_photo = os.listdir(path)
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
                text = "Вот что я умею:\n 1. /help - список всех команд.\n 2. /time - Отправить текущее дата время" \
                       "\n 3. /last - Последнее сообщение с Чатик 2.0 \n 4. /photo - Отправить случайное фото.\n" \
                       "5. Отправь фото и оно сохранится для рандомного отправления.\n" \
                       "6. /delete_photo - удалить все фотографии."
            elif text_message == '/time':
                text = current_time()
            elif text_message == '/last':
                temp = get_last_message_on_chat()
                text = f'{temp["user_name"]} : {temp["text_message"]}'
            elif text_message == '/photo':
                send_photo(chat_id)
            elif message['is_photo']:
                save_photo(message['photo'])
                text = "Фотография успешно добавлена"
            elif text_message == '/delete_photo':
                delete_all_photo()
            else:
                text = "Я не знаю такой команды"
            send_message(chat_id, text)
            last_update_id = message['last_update_id']


if __name__ == '__main__':
    main()
