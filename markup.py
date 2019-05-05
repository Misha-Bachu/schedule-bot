emoji = {'settings':'⚙️','help':'❓','list':'📜'}

def main_menu(types):
	markup = types.ReplyKeyboardMarkup(row_width=3)
	i1 = types.KeyboardButton('Заметки')
	i2 = types.KeyboardButton('Расписание')
	i3 = types.KeyboardButton('Сегодня')
	i4 = types.KeyboardButton(emoji['help'])
	i5 = types.KeyboardButton(emoji['list'])
	i6 = types.KeyboardButton(emoji['settings'])
	markup.row(i1,i2,i3)
	markup.row(i4,i5,i6)
	return markup

def settings_menu(types):
	markup = types.ReplyKeyboardMarkup(row_width=1)
	i1 = types.KeyboardButton('Изменить расписание')
	i2 = types.KeyboardButton('Предупреждать за n мин до пары')
	i3 = types.KeyboardButton('Ежедневные напоминания')
	i4 = types.KeyboardButton('Главное меню')
	markup.add(i1,i2,i3,i4)
	return markup

def change_schedule_menu(types):
	markup = types.ReplyKeyboardMarkup(row_width=2)
	i1 = types.KeyboardButton('Главное меню')
	i2 = types.KeyboardButton('Сохранить изменения расписания')
	markup.add(i1,i2)
	return markup

def help_menu(types):
	markup = types.ReplyKeyboardMarkup(row_width=2)
	i1 = types.KeyboardButton('Главное меню')
	i2 = types.KeyboardButton('Связаться с розработчиком')
	markup.add(i1,i2)
	return markup