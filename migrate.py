import constants
#import manager_db
import pygsheets
import requests
import constants

import datetime
from pytz import timezone
import telebot
import logging
from time import sleep
API_TOKEN = constants.token
telebot.logger.setLevel(logging.INFO)
logger = telebot.logger
bot = telebot.TeleBot(API_TOKEN)
month_dict={"1":"Январь","2":"Февраль","3":"Март","4":"Апрель","5":"Май","6":"Июнь","7":"Июль","8":"Август","9":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
sht = gc.open("список арендаторов")
temp_time=datetime.datetime.now()
wsheet= month_dict[str(temp_time.month)]+" "+str(temp_time.year)

wsheet1= month_dict[str(temp_time.month+1)]+" "+str(temp_time.year)

sheet = sht.worksheet('title',wsheet)#current
sheet1 = sht.worksheet('title',wsheet1)#last month

data=sheet.get_all_values()

data1=sheet1.get_all_values()


for i in range(1,len(data)):
	row_i=data[i]
	company_name=row_i[1]
	podezd=row_i[3]
	nomer_ofisa=row_i[4]
	imya=row_i[5]
	data_dogovor=row_i[7]
	dolg=row_i[20]
	for j in range(1,len(data1)):
		row_j=data1[j]
		if row_j[1]==company_name and row_j[3]==podezd and row_j[4]==nomer_ofisa and imya==row_j[5] and data_dogovor==row_j[7]:
			print(j)
			print(row_j)
			sheet1.update_cell("V"+str(j+1),dolg)#doplata
			print("FOUND")
			break
	#if row[20]!='':
	#	obw_dolg+=int(row[20])
	#print (row[17])
