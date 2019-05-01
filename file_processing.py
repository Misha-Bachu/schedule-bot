import pandas as pd

def file_proc(file_name):
	user = {}
	limit = 64 #лимит на количество записей в документе, берем первые 64 записи
	try:
		file = pd.read_excel(file_name,nrows = limit,na_values=dict,dtype=str) # получаем датафрейм
		file = file.drop_duplicates() # удаляем добликаты строк
		file = file.dropna(axis=0) # удаляем строки с пустыми ячейками
		if file.empty: # проверка на пустоту
			return user
		else:
			day = file['ДЕНЬ'].unique() # получаем все уникальные дни и формируем обьект пользователя по этим дням
			for i in day:
				user[i] = {}
			for i in file.index:
				user[file.at[i,'ДЕНЬ']][file.at[i,'ПАРА']] = {
						'ДИСЦИПЛИНА':file.at[i,'ДИСЦИПЛИНА'],
						'ТИП':file.at[i,'ТИП'],
						'АУДИТОРИЯ':file.at[i,'АУДИТОРИЯ'],
						'ПРЕПОДАВАТЕЛЬ':file.at[i,'ПРЕПОДАВАТЕЛЬ']}
	except KeyError as a:
		print(f'keyError =>{a}')
	return user