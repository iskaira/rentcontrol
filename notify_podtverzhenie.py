import telebot
import constants
import requests
from datetime import datetime
from zkdb import SQLight
from time import sleep
db=SQLight(constants.db)
bot = telebot.TeleBot(constants.token)
schedule=db.get_sobytie()
markup = telebot.types.InlineKeyboardMarkup()
row2=[telebot.types.InlineKeyboardButton("Подтвердить платеж",callback_data="/podtverdit")]	
markup.row(*row2)
managers=db.get_managers()
send_list=[]
if schedule:
	for data in schedule:
		print (data	)
		id=data[1]
		for manager in managers:
			manager_id=manager[0]
			if manager_id==id:
				send_list.append(manager_id)
send_list=list(set(send_list))
for id in send_list:
	bot.send_message(id,"<b>Пожалуйста подтвердите оплаты</b>",parse_mode="HTML",reply_markup=markup)
	sleep(0.2)
		#except Exception as e:
		#	print (e)