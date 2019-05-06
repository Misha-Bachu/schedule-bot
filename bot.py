import telebot
import requests
import pymongo
import settings
import os 
import re #для регулярок
import datetime #для работы с временем
import markup #клавиатуры
from file_processing  import file_proc # фунция которая обрабатывает документ и возвращает обьект
from user import User
from show_schedule import show, show_warn, weekday_now, lessons_time, lessons_account # функция для обработки запросов на показ расписания
from repeated_timer import RepeatedTimer # класс для создания потока

TOKEN = os.getenv("TOKEN")
ADMIN = os.getenv("ADMIN")
dict_users = {}

bot = telebot.TeleBot(TOKEN)
types = telebot.types

client = pymongo.MongoClient(f"mongodb+srv://admin:{ADMIN}@telebot-ihwsg.mongodb.net/test?retryWrites=true")
db = client.schedule_bot
users = db.users
timers = db.timers

def send_warn_mess(_id,mess,less):
	bot.send_message(_id,show_warn(mess,less),parse_mode = 'html')

def send_reminder_mess(_id,mess):
	mess = show(mess)
	bot.send_message(_id,'<b>Напоминанию, у вас завтра следующие пары:</b>',parse_mode = 'html')
	for i in mess:
		bot.send_message(_id,i,parse_mode = 'html')

def fun_warnings():
	user = users.find()
	current_time = datetime.datetime.now().time()
	day = weekday_now(datetime.date.today().weekday())
	for i in user:
		_id = i['_id']
		minute = current_time.minute + i['warn_time']
		hour = current_time.hour + minute//60
		minute = minute%60
		less = lessons_account.get(hour)
		buf = lessons_time.get(hour)
		if less:
			if not buf is None:
				if buf == minute:
					time = timers.find_one({'_id':_id})
					if time:
						less = str(less)
						buf = time.get(day)
						if buf:
							buf = buf.get(less)
							if buf:
								send_warn_mess(_id,buf,less)

def fun_reminder():
	user = users.find()
	current_time = datetime.datetime.now().time()
	day = weekday_now(datetime.date.today().weekday()+1)
	for i in user:
		_id = i['_id']
		if current_time.hour == i['daily_warn_time']['h'] and current_time.minute == i['daily_warn_time']['m']:
			time = timers.find_one({'_id':_id})
			if time:
				time = time.get(day)
				if time:
					send_reminder_mess(_id,{day : time})

rt_warnings = RepeatedTimer(60, fun_warnings)
rt_reminders = RepeatedTimer(60, fun_reminder)

print('Work hard, play hard!')

#Обработка команды старт.
@bot.message_handler(commands=['start'])
def send_start(message):
	try:
		_id = message.chat.id
		user_id = {'_id': _id}
		if not dict_users.get(_id):
				dict_users[_id] = User(id = _id)
		if not users.find_one(user_id):
			user_id.update({'warn_time':dict_users[_id].warn_time,
			'daily_warn_time':{'h':dict_users[_id].daily_warn_time.hour,'m':dict_users[_id].daily_warn_time.minute}})
			users.insert_one(user_id)
			print(f'[insert user {user_id}]')
		bot.send_message(_id,
		f'''Привет, {str(message.chat.first_name)} {str(message.chat.last_name)}.
		\nЯ бот, который поможет тебе следить за твоим расписанием. Для этого мне нужно excel файл заполненый твоими парами в таком формате:''',
		reply_markup = markup.main_menu(types))
		with open('data/img/image_example.png', 'rb') as photo:
			bot.send_photo(_id, photo)
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

# Нажатие на иконку list
@bot.message_handler(func = lambda msg: msg.text == markup.emoji['list'])
def send_list(message):
	_id = message.from_user.id
	bot.send_message(_id,'Время начала пар:')
	with open('data/img/list.jpg', 'rb') as photo:
		bot.send_photo(_id, photo)

# Обработка нажатий на кнопку "Расписание"
@bot.message_handler(func = lambda msg: msg.text == 'Расписание')
def show_schedule(message):
	_id = message.from_user.id
	user = timers.find_one({'_id':_id})
	if not user:
		bot.send_message(_id,'Вы еще не добавили расписание, добавьте его в настройках, пожалуйста.')
	else:
		user.pop('_id', None)
		mess = show(user)
		for i in mess:
			bot.send_message(message.chat.id,i,reply_markup=markup.main_menu(types),parse_mode = 'html')

# Обработка нажатий на кнопку "Сегодня"
@bot.message_handler(func = lambda msg: msg.text == 'Сегодня')
def show_schedule_today(message):
	_id = message.from_user.id
	user = timers.find_one({'_id':_id})
	if not user:
		bot.send_message(_id,'Вы еще не добавили расписание, добавьте его в настройках, пожалуйста.')
	else:
		today = datetime.date.today()
		print(f' time = {datetime.datetime.now()}')
		user = user.get(weekday_now(today.weekday()))
		if not user:
			bot.send_message(message.chat.id,'У вас нету сегодня пар.')
			return
		mess = show({weekday_now(today.weekday()):user})
		for i in mess:
			bot.send_message(message.chat.id,i,parse_mode = 'html')

# Обработка нажатий на кнопку "главное меню"
@bot.message_handler(func = lambda msg: msg.text == 'Главное меню')
def send_main_menu(message):
	bot.send_message(message.chat.id,'Главное меню:',reply_markup=markup.main_menu(types))

# Обработка нажатий на кнопку "Предупреждать за n мин до пары"
@bot.message_handler(func = lambda msg: msg.text == 'Предупреждать за n мин до пары')
def send_notice(message):
	_id = message.from_user.id
	if not dict_users.get(id):
		dict_users[_id] = User(_id)
		user = users.find_one({'_id':_id})
		if user:
			dict_users[_id].warn_time = user['warn_time']
	bot.send_message(_id,f'''
	Я буду предупреждать Вас о паре за {dict_users[_id].warn_time} минут до нее, если хотите поменять этот параметр, напишите мне время в мин максимальной длинны 3 знака, например:
	''', parse_mode = 'html',reply_markup=markup.main_menu(types))
	bot.send_message(_id,'<b>Предупреждай за 5 мин до пары</b>', parse_mode = 'html')

# Обработка нажатий на кнопку "Ежедневные напоминания"
@bot.message_handler(func = lambda msg: msg.text == 'Ежедневные напоминания')
def send_reminder(message):
	_id = message.from_user.id
	if not dict_users.get(_id):
		dict_users[_id] = User(_id)
		user = users.find_one({'_id':_id})
		if user:
			dict_users[_id].daily_warn_time = datetime.time(user['daily_warn_time']['h'],user['daily_warn_time']['m'])
	bot.send_message(message.chat.id,f'''
	Я буду напоминать Вам о следующих парах каждый день в {dict_users[_id].daily_warn_time}. Если хотите поменять этот параметр, отправьте мне, напишите мне время например:
	''', parse_mode = 'html',reply_markup=markup.main_menu(types))
	bot.send_message(_id,'<b>Ежедневные напоминания в 20:30</b>', parse_mode = 'html')


# Обработака нажатия на "связаться с розработчиком"
@bot.message_handler(func = lambda msg: msg.text == 'Связаться с розработчиком')
def get_dev_name(message):
	bot.send_message(message.chat.id,'''Меня создал @Misha_Bachu, если Вы заметили проблемы 
	в моей работе, пожалуйста, сообщите ему об этом.''',reply_markup=markup.main_menu(types))

# Обработака фразы "Предупреждай за n мин до пары"
@bot.message_handler(regexp = r"Предупреждай за \d{1,3} мин до пары")
def set_warn_time(message):
	print(message.text)
	_id = message.from_user.id
	warn_time = int(re.findall(r' \d{1,3} ',message.text)[0])
	user = users.find_one({'_id':_id})
	if not dict_users.get(_id):
		dict_users[_id] = User(_id, warn_time = warn_time)
		if not user:
			users.insert_one({'_id': _id,'warn_time':warn_time, 'daily_warn_time':{'h':dict_users[_id].daily_warn_time.hour,'m':dict_users[_id].daily_warn_time.minute}})
	else:
		dict_users[_id].warn_time = warn_time
		users.update_one(user,{"$set":{'warn_time':warn_time}})
	bot.send_message(_id,f'''Хорошо, теперь я буду Вас предупреждать за {warn_time} мин до пар.''',reply_markup=markup.main_menu(types))

# Обработака фразы "Ежедневные напоминания в hh:mm"
@bot.message_handler(regexp = r"Ежедневные напоминания в \d{1,2}:\d{1,2}")
def set_daily_warn_time(message):
	print(message.text)
	_id = message.chat.id
	result = re.findall(r'\d{1,2}:\d{1,2}',message.text)
	h,m = str(result[0]).split(':')
	h,m = int(h),int(m)
	if h<0 or h>23 or m<0 or m>59:
		bot.send_message(_id,'Вы ввели некорректное время. Повторите, пожалуйста')
	else:
		daily_warn_time = datetime.time(h,m)
		user = users.find_one({'_id':_id})
		if not dict_users.get(_id):
			dict_users[_id] = User(_id,daily_warn_time = daily_warn_time)
		if not user:
			users.insert_one({'_id': _id,'warn_time':dict_users[_id].warn_time, 'daily_warn_time':{'h':h,'m':m}})
		else:
			dict_users[_id].daily_warn_time = daily_warn_time
			users.update_one(user,{"$set":{'daily_warn_time':{'h':h,'m':m}}})
		bot.send_message(_id,f'''Хорошо, теперь я буду Вам напоминать о завтрашних парах {daily_warn_time} каждый день.''',reply_markup=markup.main_menu(types))

# изменение расписания
@bot.message_handler(func = lambda msg: msg.text == 'Изменить расписание')
def send_schedule(message):
	try:
		_id = message.chat.id
		bot.send_message(_id,'Загрузите новый excel файл(старый файл перестанет быть действительным) в таком формате:'
		,reply_markup=markup.change_schedule_menu(types))
		with open('data/img/image_example.png', 'rb') as photo:
			bot.send_photo(_id, photo)
	except IOError:
		print("An IOError has occurred!")

# нажатия на кнопку "Пример файла"
@bot.message_handler(func = lambda msg: msg.text == 'Пример файла')
def send_example_schedule(message):
	try:
		_id = message.chat.id
		bot.send_message(_id,'Фармат файла excel должен быть .xlsx (в дальнейшем будут поддержеваться и другие фоматы)')
		with open('data/example.xlsx', 'rb') as file:
			bot.send_document(_id, file)
	except IOError:
		print("An IOError has occurred!")

# нажатия на кнопку "Заметки"
@bot.message_handler(func = lambda msg: msg.text == 'Заметки')
def send_notes(message):
		bot.send_message(message.chat.id,'Реализация этой фунции будет чуть позже.')

# Сохранить изменения расписания
@bot.message_handler(func = lambda msg: msg.text == 'Сохранить изменения расписания')
def save_schedule(message):
	try:
		_id = message.from_user.id
		if not dict_users.get(_id):
			dict_users[_id] = User(_id)
		if not dict_users[_id].get_schedule():
			bot.send_message(_id,'Загрузите файл еще раз, я ничего не получил или соединение прервалось и потерялись данные.')
		else:
			timers.replace_one({'_id':_id},dict_users[_id].get_schedule(),upsert=True)
			bot.send_message(_id,'Спасибо, ваше новое расписание сохранено.',reply_markup=markup.main_menu(types))
	except IOError:
		print(f"An IOError has occurred => {IOError}")
	except KeyError:
		print(f'KeyError => {KeyError}')

#сохранение документа с расписанием
@bot.message_handler(content_types=['document'])
def handle_docs(message):
	try:
		_id = message.chat.id
		from data.mime_type import mime_type #Загружаем словарь мим типов
		if mime_type['.xlsx'] == message.document.mime_type: #Проверка типа файла.
			bot.send_message(_id,'Спасибо, Ваш файл обрабатывается.')
			file_info = bot.get_file(message.document.file_id)
			file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path)) # Получаем сам файл.
			file_name = str(message.from_user.id)+str(message.from_user.username)+'.xlsx' #Формируем название будущего файла с пользователя и имя пользователя
			with open(file_name, 'wb') as fd: #Открываем\создаем и записываем в файл.
				for chunk in file.iter_content(chunk_size=128):
					fd.write(chunk)
			user_time = file_proc(file_name) #отправляем файл в обработку, нам вернет пустой словарь если все плохо и заполненый если все хорошо
			if user_time == {}:
				bot.send_message(_id,'Ваш файл не подходит мне, пришлите, пожалуйста, файл в таком формате.',reply_markup=markup.change_schedule_menu(types))
				with open('data/img/image_example.png', 'rb') as photo:
					bot.send_photo(_id, photo)
			else:
				if not dict_users.get(_id):
					dict_users[_id] = User(_id)
				dict_users[_id].set_user_schedule(user_time)
				bot.send_message(_id,'Ваш файл полностью подходит мне, сохраните изменения расписания.',reply_markup=markup.change_schedule_menu(types))
		else:
			bot.send_message(_id,'Этот файл мне не подходит.',reply_markup=markup.change_schedule_menu(types))
	except IOError:
		print("An IOError has occurred!")

# обработка всех оставшихся ситуаций
@bot.message_handler(func = lambda message:True)
def upper(message):
	bot.reply_to(message,'Извините, я Вас не понимаю. Пользуйтесь, пожалуйста, пользовательской клавиатурой.')

bot.polling()