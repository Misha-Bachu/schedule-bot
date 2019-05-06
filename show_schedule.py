emoji = {'1':'1️⃣','2':'2️⃣','3':'3️⃣','4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣','8':'8️⃣','warn':'❗️'}
weekday_now = lambda date: ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье'][date]
lessons_time = {8:0,9:45,11:15,12:45,14:15,15:45,17:15,18:45}
lessons_account = {8:1,9:2,11:3,12:4,14:5,15:6,17:7,18:8}

def show (user):
	arr = []
	for i in user:
		mess = f'{ emoji["warn"] }<b>{i}</b>{emoji["warn"]}\n'
		for j in user[i]:
			buf = user[i][j]
			mess = mess + emoji[j] +' ' + buf['ДИСЦИПЛИНА'] +' в '+ buf['АУДИТОРИЯ']+' аудитории, '+buf['ТИП'] + '.\nПреподаватель '+buf['ПРЕПОДАВАТЕЛЬ']+'\n\n'
		arr.append(mess)
		mess = ''
	return arr

def show_warn (user,less):
	mess = f'{ emoji["warn"] }<b>У вас скоро пара</b>{emoji["warn"]}\n'
	mess = mess + emoji[less] +' ' + user['ДИСЦИПЛИНА'] +' в '+ user['АУДИТОРИЯ']+' аудитории, '+user['ТИП'] + '.\nПреподаватель '+user['ПРЕПОДАВАТЕЛЬ']
	return mess