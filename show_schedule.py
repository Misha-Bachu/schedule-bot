emoji = {'1':'1️⃣','2':'2️⃣','3':'3️⃣','4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣','8':'8️⃣','warn':'❗️'}


# lesson_ru = lambda i: ['Первая пара: ','Вторая пара: ','Третья пара: ','Четвертая пара: ','Пятая пара: ','Шестая пара: ','Седьмая пара: ','Восьмая пара: '][int(i)-1]
weekday_now = lambda date: ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье'][date.weekday()]

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