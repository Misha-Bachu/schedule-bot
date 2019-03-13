import telebot
import requests
import settings
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

#Обработка команды старт.
@bot.message_handler(commands=['start'])
def send_hello(message):
	chat_id = message.chat.id
	bot.send_message(chat_id,'Привет, {0} {1}.\nЯ бот, который поможет тебе следить за твоим рассписанием.'
	.format(str(message.chat.first_name), str(message.chat.last_name)))
	bot.send_message(chat_id,'Для этого мне нужно excel файл заполненый твоими парами в таком формате:'.format())
	photo = open('data/img/image_example.png', 'rb')
	bot.send_photo(chat_id, photo)

@bot.message_handler(func = lambda message:True)
def upper(message):
	bot.reply_to(message,'This bot is in development, turn it off for a while.')
	#bot.send_message(message.chat.id,'lol',parse_mode='html',)
	#bot.edit_message_text('lol',message.chat.id,message.message_id-1)
	print(message.json)
	#bot.send_document(message.chat.id,open('test.xlsx', 'rb'),caption='lolkin anabolkin',disable_notification=False) #отправка файла

#сохранение документов файла
@bot.message_handler(content_types=['document'])
def handle_docs(message):
	print(message.json)
	#Загружаем словарь мим типов
	from data.mime_type import mime_type
	#Проверка типа файла.
	if mime_type['.xlsx'] == message.document.mime_type:
		bot.send_message(message.chat.id,'Спасибо, твой файл обрабатывается.')
		file_info = bot.get_file(message.document.file_id)
		#Получаем сам файл.
		file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
		#Формируем название будущего файла с пользователя и имя пользователя
		file_name = str(message.from_user.id)+str(message.from_user.username)+'.xlsx'
		#Открываем\создаем и записываем в файл.
		with open(file_name, 'wb') as fd:
			for chunk in file.iter_content(chunk_size=128):
				fd.write(chunk)
	else:
		bot.send_message(message.chat.id,'Этот файл мне не подходит.')
bot.polling()