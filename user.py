import datetime
class User:
	#конструктор
	def __init__(self,id, warn_time = 30,daily_warn_time = datetime.time(20,30)):
		self.__id = id
		self.warn_time = warn_time
		self.daily_warn_time = daily_warn_time

	def set_user_schedule(self,obj):
		self.schedule = obj

	def get_schedule(self):
		try:
			return self.schedule
		except AttributeError:
			return False

	#для вивода в консоль
	def __str__(self):
		return f'[User {self.__id} => {self.warn_time} and {self.daily_warn_time}]'
	#диструктор
	def __del__(self):
		print(f'[User {self.__id} removed from memory app.]')