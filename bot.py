import telebot
import requests
import pymongo
import settings
import os 
import markup #клавиатуры
import re #для регулярок
import datetime #для работы с временем

TOKEN = os.getenv("TOKEN")
ADMIN = os.getenv("ADMIN")
warn_time = 30
daily_warn_time = datetime.time(20,30)

bot = telebot.TeleBot(TOKEN)
types = telebot.types

client = pymongo.MongoClient(f"mongodb+srv://admin:{ADMIN}@telebot-ihwsg.mongodb.net/test?retryWrites=true")
db = client.schedule_bot
users = db.users
print('==========================================================')

#Обработка команды старт.
@bot.message_handler(commands=['start'])
def send_start(message):
	try:
		chat_id = message.chat.id
		user_id = {'_id': message.from_user.id,'warn_time':warn_time, 'daily_warn_time':daily_warn_time}
		if not users.find_one(user_id):
			users.insert_one(user_id)
			print(f'insert user {user_id}')
		bot.send_message(chat_id,
		f'''Привет, {str(message.chat.first_name)} {str(message.chat.last_name)}.
		\nЯ бот, который поможет тебе следить за твоим расписанием. Для этого мне нужно excel файл заполненый твоими парами в таком формате:''',
		reply_markup = markup.main_menu(types))
		with open('data/img/image_example.png', 'rb') as photo:
			bot.send_photo(chat_id, photo)
	except IOError:
		print("An IOError has occurred!")

# Нажатие на иконку помощи или ввод команды help
@bot.message_handler(commands=['help'])
@bot.message_handler(func = lambda msg: msg.text == markup.emoji['help'])
def send_help_markup(message):
	bot.send_message(message.chat.id,'Помощь:',reply_markup=markup.help_menu(types))

# Нажатие на иконку настроек или ввод команды settings
@bot.message_handler(commands=['settings'])
@bot.message_handler(func = lambda msg: msg.text == markup.emoji['settings'])
def send_settings_markup(message):
	bot.send_message(message.chat.id,'Настройки:',reply_markup=markup.settings_menu(types))

# Обработка нажатий на кнопку "главное меню"
@bot.message_handler(func = lambda msg: msg.text == 'Главное меню')
def send_main_menu(message):
	bot.send_message(message.chat.id,'Главное меню:',reply_markup=markup.main_menu(types))

# Обработка нажатий на кнопку "Предупреждать за n мин до пары"
@bot.message_handler(func = lambda msg: msg.text == 'Предупреждать за n мин до пары')
def send_notice(message):
	bot.send_message(message.chat.id,f'''
	Я буду предупреждать Вас о паре за {warn_time} минут до нее, если хотите поменять этот параметр, напишите мне время в мин максимальной длинны 3 знака, например:\n<b>Предупреждай за 5 мин до пары</b>
	''', parse_mode = 'html',reply_markup=markup.main_menu(types))

# Обработака фразы "Предупреждай за n мин до пары"
@bot.message_handler(regexp = r"Предупреждай за \d{1,3} мин до пары")
def set_warn_time(message):
	print(message.text)
	warn_time = int(re.findall(r' \d{1,3} ',message.text)[0])
	user_id = {'_id': message.from_user.id}
	bot.send_message(message.chat.id,f'''Хорошо, теперь я буду Вас предупреждать за {warn_time} мин до пар.''',reply_markup=markup.main_menu(types))

# Обработка нажатий на кнопку "Ежедневные напоминания"
@bot.message_handler(func = lambda msg: msg.text == 'Ежедневные напоминания')
def send_reminder(message):
	bot.send_message(message.chat.id,f'''
	Я буду напоминать Вам о следующих парах каждый день в {daily_warn_time}. Если хотите поменять этот параметр, отправьте мне, напишите мне время например:\n<b>Ежедневные напоминания в 20:30</b>
	''', parse_mode = 'html',reply_markup=markup.main_menu(types))

# Обработака фразы "Ежедневные напоминания в hh:mm"
@bot.message_handler(regexp = r"Ежедневные напоминания в \d{1,2}:\d{1,2}")
def set_daily_warn_time(message):
	print(message.text)
	result = re.findall(r'\d{1,2}:\d{1,2}',message.text)
	h,m = str(result[0]).split(':')
	h,m = int(h),int(m)
	if h<0 or h>23 or m<0 or m>59:
		bot.send_message(message.chat.id,'Вы ввели некорректное время. Повторите, пожалуйста')
	else:
		daily_warn_time = datetime.time(h,m)
		bot.send_message(message.chat.id,f'''Хорошо, теперь я буду Вам напоминать о парах в {daily_warn_time} каждый день.''',reply_markup=markup.main_menu(types))

# Обработака нажатия на "связаться с розработчиком"
@bot.message_handler(func = lambda msg: msg.text == 'Связаться с розработчиком')
def get_dev_name(message):
	bot.send_message(message.chat.id,'''Меня создал @Misha_Bachu, если Вы заметили проблемы 
	в моей работе, пожалуйста, сообщите ему об этом.''',reply_markup=markup.main_menu(types))

# изменение расписания
@bot.message_handler(func = lambda msg: msg.text == 'Изменить расписание')
def send_schedule(message):
	try:
		bot.send_message(message.chat.id,'Загрузите новый excel файл(старый файл перестанет быть действительным) в таком формате:'
		,reply_markup=markup.change_schedule_menu(types))
		with open('data/img/image_example.png', 'rb') as photo:
			bot.send_photo(message.chat.id, photo)
	except IOError:
		print("An IOError has occurred!")

#сохранение документа с расписанием
@bot.message_handler(content_types=['document'])
def handle_docs(message):
	try:
		print(message.json)
		#Загружаем словарь мим типов
		from data.mime_type import mime_type
		#Проверка типа файла.
		if mime_type['.xlsx'] == message.document.mime_type:
			bot.send_message(message.chat.id,'Спасибо, Ваш файл обрабатывается.')
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
			bot.send_message(message.chat.id,'Этот файл мне не подходит.',reply_markup=markup.change_schedule_menu(types))
	except IOError:
		print("An IOError has occurred!")

# обработка всех оставшихся ситуаций
@bot.message_handler(func = lambda message:True)
def upper(message):
	bot.reply_to(message,'Извините, я Вас не понимаю. Пользуйтесь, пожалуйста, пользовательской клавиатурой.')
	#bot.send_message(message.chat.id,'lol',parse_mode='html',)
	#bot.edit_message_text('lol',message.chat.id,message.message_id-1)
	#print(message.json)
	#bot.send_document(message.chat.id,open('test.xlsx', 'rb'),caption='lolkin anabolkin',disable_notification=False) #отправка файла

bot.polling()