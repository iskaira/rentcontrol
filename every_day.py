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
sheet = sht.worksheet('title',wsheet)
data=sheet.get_all_values()
print (data)
	
'''
Наименование арендатора: ТОО Жетысу Алматы
Номер офиса: 6 
Имеет задолженность в размере 150000 тг 
Дата договора: 1/16/2018 ->02.12.2018
*Просрочено на  4 дней/дня*

date='2/2/2018'
>>> 

'''

def check_date_expiration(row_id,expire_date,company_name,nomer_ofisa,arenda,imya,phone,dolg):
	current="%Y-%m-%d"
	now_time = datetime.datetime.now().day
	exp_date=int(expire_date.split('/')[1])
	if exp_date<8:
		exp_date+=30
	raznica=exp_date-now_time
	print(raznica)
	message_info=''
	exp=expire_date.split('/')
	new_expire=exp[1]+'-'+exp[0]+'-'+exp[2]

	if 0<(raznica)<=3:
		if raznica==1:
			message_info+='*До оплаты '+str(raznica)+' день*\n\n'
		else:
			message_info+='*До оплаты '+str(raznica)+' дня*\n\n'
		message_info+='Наименование арендатора: '+'*'+company_name+'*\n'
		message_info+='Номер офиса: '+'*'+str(nomer_ofisa)+'*\n'
		message_info+='Оплата за аренду: '+'*'+str(dolg)+' тг*\n'#dolg lu4we
		message_info+='Оплачено до: '+'*'+new_expire+'*\n'#dolg lu4we
		message_info+='Имя арендатора: '+'*'+imya+'*\n'#dolg lu4we
		message_info+='Номер арендатора: '+phone+'\n'#dolg lu4we
		bot.send_message(295091909,message_info,parse_mode='MARKDOWN')
		#print("Здравствуйте! "+company_name+" офис: "+nomer_ofisa+" должен оплатить аренду в размере "+arenda+" "+date+" "+imya+" "+phone)
	elif -15<raznica<0:
		if raznica==4:
			message_info+='*Задолженность на '+str(abs(raznica))+' дня*\n\n'
		else:
			message_info+='*Задолженность на '+str(abs(raznica))+' дней*\n\n'
		message_info+='Наименование арендатора: '+'*'+company_name+'*\n'
		message_info+='Номер офиса: '+'*'+str(nomer_ofisa)+'*\n'
		message_info+='Оплата за аренду: '+'*'+str(dolg)+' тг*\n'#dolg lu4we
		message_info+='Дата оплаты: '+'*'+new_expire+'*\n'#dolg lu4we
		bot.send_message(295091909,message_info,parse_mode='MARKDOWN')
	elif raznica==0:
		#sheet.update_cell('R2'+str(row_id),dolg+arenda)#Подумать
		message_info+='*Задолженность на '+str(raznica)+' дней*\n\n'
		message_info+='Наименование арендатора: '+'*'+company_name+'*\n'
		message_info+='Номер офиса: '+'*'+str(nomer_ofisa)+'*\n'
		message_info+='Оплата за аренду: '+'*'+str(dolg)+' тг*\n'#dolg lu4we
		message_info+='Дата оплаты: '+'*'+new_expire+'*\n'#dolg lu4we
		bot.send_message(295091909,message_info,parse_mode='MARKDOWN')

		#oplatil vsego	
		#message_info+='Имя арендатора: '+'*'+imya+'*\n'#dolg lu4we
		#message_info+='Номер арендатора: '+phone+'\n'#dolg lu4we
		#print("Здравствуйте! "+company_name+" офис: "+nomer_ofisa+" имеет задолженность в размере "+arenda+" "+date+" просрочено на "+str(raznica)+" дня/дней")
	elif raznica<=-15:
		message_info+='*Задолженность на '+str(abs(raznica))+' ДНЕЙ !!! Возможно стоит рассмотреть расторжение договора*\n\n'
		message_info+='Наименование арендатора: '+'*'+company_name+'*\n'
		message_info+='Номер офиса: '+'*'+str(nomer_ofisa)+'*\n'
		message_info+='Имя арендатора: '+'*'+imya+'*\n'#dolg lu4we
		message_info+='Номер арендатора: '+phone+'\n'#dolg lu4we
		message_info+='Задолженность: '+'*'+str(dolg)+' тг*\n'#dolg lu4we
		message_info+='Дата оплаты: '+'*'+new_expire+'*\n'#dolg lu4we
		bot.send_message(295091909,message_info,parse_mode='MARKDOWN')
obw_dolg=0
for i in range(1,len(data)-1):
	row=data[i]
	row_id=row[0]
	company_name=row[1]
	podezd=row[3]
	nomer_ofisa=row[4]
	imya=row[5]
	phone=row[6]
	date=row[7]
	arenda=row[9]
	dolg=row[20]
	if row[20]!='':
		obw_dolg+=int(row[20])
	#print (row[17])
	check_date_expiration(row_id,date,company_name,nomer_ofisa,arenda,imya,phone,dolg)
	sleep(0.3)
bot.send_message(295091909,"Общая задолженность равна на сегодняшний день равна: <b>"+str(obw_dolg)+' тг</b>',parse_mode="HTML")


#№ п/п	ФИО, наименование арендатора	номер договора	подъезд	номер офиса	Имя представителя	Номер представителя	дата договора	деятельность	аренда	Оплачено (да/нет)	Оплата 1	Подтверждение 1 оплаты	Оплата 2	Подтверждение оплаты 2	Оплата 3	Задолженность
#1	ТОО ADEM PRINT	120/1-1	1	1	Адема	8-701-244-0004	6/7/2017	типогрфия услуги	150000							
'''
for i in range(1,len(data)-1):
			row=data[i]
			row_id=row[0]
			company_name=row[1]
			podezd=row[3]
			nomer_ofisa=row[4]
			imya=row[5]
			phone=row[6]
			date=row[7]
			arenda=row[9]
			opla4eno=row[19]
			dolg=row[20]
			zadolzhennost=row[21]
			if row_id!='' and company_name!='':
				info=check_date_expiration(row_id,imya,nomer_ofisa,date,dolg,zadolzhennost)
				if len(info)>0:
					arendatory+='*'+info[0]+" Nº: "+info[1]+'*\n'
					summa_arendy+=int(info[2])
					if info[3]!='':
						obw_dolg+=int(info[3])
				sleep(0.2)
'''