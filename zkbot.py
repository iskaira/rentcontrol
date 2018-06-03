#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from time import sleep
import constants
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pygsheets
from threading import Thread
import datetime
import requests
from zkdb import SQLight
API_TOKEN = constants.token
telebot.logger.setLevel(logging.INFO)
logger = telebot.logger
bot = telebot.TeleBot(API_TOKEN)
#gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
#sht = gc.open("список арендаторов")
#sheet = sht.worksheet('title','Sheet1')
#data=sheet.get_all_values()
#print("DONE KNOPKI")

oplata_dict = {}
approve_dict= {}
class Oplata:
    def __init__(self, podezd):
        self.podezd = podezd
        self.ofis = None
        self.arendator = None
        self.price = None
class Approve:
    def __init__(self, data):
        self.data = data
        self.photo = None



def update_knopki():
	gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
	sht = gc.open("список арендаторов")
	month_dict={"1":"Январь","2":"Февраль","3":"Март","4":"Апрель","5":"Май","6":"Июнь","7":"Июль","8":"Август","9":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
	month_dict0={"01":"Январь","02":"Февраль","03":"Март","04":"Апрель","05":"Май","06":"Июнь","07":"Июль","08":"Август","09":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}

	temp_time=datetime.datetime.now()
	wsheet= month_dict[str(temp_time.month)]+" "+str(temp_time.year)
	sheet = sht.worksheet('title',wsheet)
	data=sheet.get_all_values()
	print (data)
	db=SQLight(constants.db)
	db.delete()
	for i in range(1,len(data)-1):
		row=data[i]#row[3] - podezd row[4] - nomer ofisa row[5] - imya
		if row[3]!='':
			db.insert(row[3],row[4],row[5])
	print("DONE KNOPKI")
	db.close()

def to_normal_price(price):
	line=str(price)
	n = 3
	length=len(line)
	t=''
	if length%3==0:
		temp=([line[i:i+n] for i in range(0, len(line), n)])
		for i in temp:
			t+=i+'.'
	if length%3==2:
		temp=([line[i:i+n] for i in range(2, len(line), n)])
		t+=line[:2]+'.'
		for i in temp:
			t+=i+'.'
	if length%3==1:
		temp=([line[i:i+n] for i in range(1, len(line), n)])
		t+=line[0]+'.'
		for i in temp:
			t+=i+'.'
	return (t[:-1])


update_knopki()

def menu_message(id,message_id=None):
	markup = telebot.types.InlineKeyboardMarkup()
	row1=[telebot.types.InlineKeyboardButton("Принять платеж",callback_data="/oplata")]
	row2=[telebot.types.InlineKeyboardButton("Подтвердить платеж",callback_data="/podtverdit")]	
	row3=[telebot.types.InlineKeyboardButton("Что ожидается?",callback_data="/ozhidanie")]	
	
	markup.row(*row1)
	markup.row(*row2)
	markup.row(*row3)
	message_text="Вы в главном меню "+u"\U0001F3AF"+"\n\n" + "* Чтобы сделать платеж по оплату клиента нажмите на кнопку \n[ Принять платеж ]\n* Чтобы подтвердить платеж клиента нажмите на кнопку \n[ Подтвердить платеж ]"
	try:
		bot.edit_message_text(message_text, id, message_id,parse_mode='HTML',reply_markup=markup)
		return
	except:
		print('cant')
	bot.send_message(id,message_text,reply_markup=markup)
	print ('[STARTED Conversation]')
	print (id)
	
@bot.message_handler(commands=['start'])
def starting(message):
	print ('[STARTED Conversation]')
	print (message.from_user.id)
	whitelist=[]#295091909
	menu_message(message.from_user.id)
	update_knopki()
	

@bot.callback_query_handler(func=lambda call: call.data == '/oplata')
def process_oplata(call):
	try:
		db=SQLight(constants.db)
		buttons=db.get_podezd()
		podezd_markup = telebot.types.InlineKeyboardMarkup()
		for button in buttons:
			if button=='подвал':
				row=[telebot.types.InlineKeyboardButton(button,callback_data="podezd"+button)]
			else:
				row=[telebot.types.InlineKeyboardButton(button+" подъезд",callback_data="podezd"+button)]
			podezd_markup.row(*row)
		podezd_markup.row(telebot.types.InlineKeyboardButton("Отменить",callback_data="nazadmenu"))
		bot.edit_message_text("<b>Выберите подъезд:</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=podezd_markup)
		db.close()
	except Exception as e:
		bot.send_message(call.from_user.id,"process_oplata step: "+str(e))

@bot.callback_query_handler(func=lambda call: call.data[:6] == 'podezd')
def process_podezd(call):
	try:
		db=SQLight(constants.db)
		podezd=call.data[6:]
		oplata = Oplata(podezd)
		chat_id=call.from_user.id
		oplata_dict[chat_id] = oplata
		buttons=db.get_ofis(podezd)
		ofis_markup = telebot.types.InlineKeyboardMarkup()
		for button in buttons:
			row=[telebot.types.InlineKeyboardButton(button+" офис",callback_data="ofis"+button)]
			ofis_markup.row(*row)
		ofis_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadoplata"))
		bot.edit_message_text("<b>Выберите номер офиса:</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=ofis_markup)
	except Exception as e:
		bot.send_message(call.from_user.id,"process_podezd step: "+str(e))

@bot.callback_query_handler(func=lambda call: call.data[:4] == 'ofis')
def process_ofis(call):
	try:
		db=SQLight(constants.db)
		ofis=call.data[4:]
		chat_id=call.from_user.id
		try:
			oplata=oplata_dict[chat_id]
		except:
			#bot.send_message(chat_id,"Заполните заново, не смогли найти ваши предидущие данные, возможно сервер перезагрузился")
			menu_message(chat_id,call.message.message_id)
			return
		oplata.ofis=ofis
		buttons=db.get_arendator(oplata.podezd,oplata.ofis)
		#print (buttons)
		arendator_markup = telebot.types.InlineKeyboardMarkup()
		for button in buttons:
			row=[telebot.types.InlineKeyboardButton(button,callback_data="arenda"+button)]
			arendator_markup.row(*row)
		arendator_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadpodezd"))
		msg=bot.edit_message_text("<b>Выберите арендатора:</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=arendator_markup)
	except Exception as e:
		bot.send_message(call.from_user.id,"process_ofis step: "+str(e))
@bot.callback_query_handler(func=lambda call: call.data[:6] == 'arenda')
def process_arendator(call):
	try:
		#db=SQLight(constants.db)
		arendator=call.data[6:]
		chat_id=call.from_user.id
		try:
			oplata=oplata_dict[chat_id]
		except:
			#bot.send_message(chat_id,"Заполните заново, не смогли найти ваши предидущие данные, возможно сервер перезагрузился")
			menu_message(chat_id,call.message.message_id)
			return
		oplata.arendator=arendator
		arendator_markup = telebot.types.InlineKeyboardMarkup()
		arendator_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadofis"))
		msg=bot.edit_message_text("<b>Введите сумму платежа:</b>\n/back Чтобы вернуться назад", call.from_user.id, call.message.message_id,parse_mode='HTML')
		bot.register_next_step_handler(msg, process_price)
			
	except Exception as e:
		bot.send_message(call.from_user.id,"Process_arendator step: "+str(e))

def process_price(message):
	try:
		chat_id = message.from_user.id
		price = message.text
		if price=='/back':
			oplata=oplata_dict[chat_id]
			db=SQLight(constants.db)
			buttons=db.get_arendator(oplata.podezd,oplata.ofis)
			arendator_markup = telebot.types.InlineKeyboardMarkup()
			for button in buttons:
				row=[telebot.types.InlineKeyboardButton(button,callback_data="arenda"+button)]
				arendator_markup.row(*row)
			arendator_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadofis"))
			bot.send_message(chat_id,"<b>Выберите арендатора:</b>",parse_mode='HTML',reply_markup=arendator_markup)
			return
		try:
			price=int(price)#"", call.from_user.id, call.message.message_id,
		except:
			msg=bot.reply_to(message,"Оплата должна быть в цифрах!!!\n<b>Введите сумму платежа:</b>\n/back Чтобы вернуться назад",parse_mode='HTML')
			bot.register_next_step_handler(msg, process_price)
			return	
		try:
			oplata=oplata_dict[chat_id]
		except:
			#bot.send_message(chat_id,"Заполните заново, не смогли найти ваши предидущие данные, возможно сервер перезагрузился")
			menu_message(chat_id,call.message.message_id)
			return
		
		markup = telebot.types.InlineKeyboardMarkup()
		row1=[telebot.types.InlineKeyboardButton("ДА",callback_data="oplatada"),telebot.types.InlineKeyboardButton("НЕТ",callback_data="oplatanet")]
		markup.row(*row1)
		t=to_normal_price(price)
		oplata.price=price
		msg =  bot.send_message(chat_id, 'Вы приняли <b>'+t+'</b> тенге?',parse_mode='HTML',reply_markup=markup)
	except Exception as e:
		print(e)
		bot.send_message(message.from_user.id, 'Опаньки что-то пошло не так, посмотрите, верно ли ответили тому, что запросил бот...')
		bot.send_message(295091909,'Опаньки что-то пошло не так в process_client_price: '+str(e)+" From:"+message.from_user.username)



@bot.callback_query_handler(func=lambda call: call.data in ['oplatada','oplatanet'])
def process_yes_no(call):
	#try:
	chat_id=call.from_user.id
	try:
		oplata=oplata_dict[chat_id]
	except:
		bot.send_message(chat_id,"Пожалуйста заполните заново, не смогли найти ваши предидущие данные, возможно сервер перезагрузился")
		menu_message(chat_id,call.message.message_id)
		return
	if call.data=='oplatada':
		db=SQLight(constants.db)
		now_time = datetime.datetime.now()
		db.add_sobytie(call.from_user.id,oplata.podezd,oplata.ofis,oplata.arendator,oplata.price,now_time)
		
		bot.edit_message_text("Вы красавчик, продолжайте работать!",chat_id,call.message.message_id)
		menu_message(chat_id)
		gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
		try:
			sht = gc.open("список арендаторов")
		except Exception as e:
			print("CANT OPEN GOOGLE SHEET",e)
			sleep(30)
			sht = gc.open("список арендаторов")
		
		month_dict={"1":"Январь","2":"Февраль","3":"Март","4":"Апрель","5":"Май","6":"Июнь","7":"Июль","8":"Август","9":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
		temp_time=datetime.datetime.now()
		wsheet= month_dict[str(temp_time.month)]+" "+str(temp_time.year)			
		try:
			sheet = sht.worksheet('title',wsheet)
		except Exception as e:
			print("CANT OPEN GOOGLE WORKSHEET",e)
			sleep(30)
			sheet = sht.worksheet('title',wsheet)
		data=sheet.get_all_values()
		row_num=-1
		row_info=[]
		for i in range(1,len(data)-1):
			row=data[i]
			if row[3]==oplata.podezd and row[4]==oplata.ofis and row[5]==oplata.arendator:		
				#print(i,"HELLO")
				row_num=i+1
				row_info=row
				break
		print(row_num)
		print(row_info)
		opl=0
		letter_dict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"AA",27:"AB",28:"AC",29:"AD",30:"AE"}

		for i in range(11,20,3):
			if row_info[i]=='':
				dpl=i-11
				print(dpl)
				break
		sheet.update_cell(letter_dict[11+dpl]+str(row_num),str(oplata.price))#doplata
		sheet.update_cell(letter_dict[12+dpl]+str(row_num),str(now_time))#doplata
		managers=db.get_managers()
		for manager in managers:
			manager_id=manager[0]
			#if manager_id!=call.from_user.id:
			sleep(0.2)
			bot.send_message(manager_id,"Пожалуйста подтвердите оплату менеджера <b>"+call.from_user.first_name+"</b> \nАрендатор: <b>"+oplata.arendator+" Nº:"+oplata.ofis+"</b>\nСумма: <b>"+str(oplata.price)+" тенге</b>",parse_mode="HTML")
			#319813384 Daulet
			
		oplata.podezd=None
		oplata.ofis=None
		oplata.arendator=None
		oplata.price=None
	else:
		msg=bot.edit_message_text("<b>Введите сумму платежа:</b>\n/back Чтобы вернуться назад", call.from_user.id, call.message.message_id,parse_mode='HTML')
		bot.register_next_step_handler(msg, process_price)
	'''
	except Exception as e:
		print(e)
		bot.send_message(295091909,"process_client_yes_no: "+str(e)+" From:"+call.from_user.username)
	'''


def check_date_expiration(row_id,imya,ofis,expire_date,dolg,zadolzhennost):
	try:
		current="%Y-%m-%d"
		now_time = datetime.datetime.now().day
		#oplacheno=False
		expire_date=int(expire_date.split('/')[1])
		if expire_date<8:
			expire_date+=30
		raznica=expire_date-now_time
		print(raznica)
		otchet=[]
		if 0<(raznica)<=7 and int(dolg)>=0:
			otchet.append(imya)
			otchet.append(ofis)
			otchet.append(dolg)
			otchet.append(zadolzhennost)
		return otchet
	except Exception as e:
		print (e)



@bot.callback_query_handler(func=lambda call: call.data == '/ozhidanie')
def process_ozhidanie(call):
	try:
		gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
		sht = gc.open("список арендаторов")
		month_dict={"01":"Январь","02":"Февраль","03":"Март","04":"Апрель","05":"Май","06":"Июнь","07":"Июль","08":"Август","09":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
		current="%Y-%m-%d"
		now_time=datetime.datetime.now()
		current_time=now_time.strftime(current).split("-")
		wsheet= month_dict[current_time[1]]+" "+str(current_time[0])
		sheet = sht.worksheet('title',wsheet)
		data=sheet.get_all_values()
		obw_dolg=0
		arendatory=''
		summa_arendy=0
		markup = telebot.types.InlineKeyboardMarkup()
		row1=[telebot.types.InlineKeyboardButton("Принять платеж",callback_data="/oplata")]
		row2=[telebot.types.InlineKeyboardButton("Подтвердить платеж",callback_data="/podtverdit")]	
		row3=[telebot.types.InlineKeyboardButton("Что ожидается?",callback_data="/ozhidanie")]	
		
		markup.row(*row1)
		markup.row(*row2)
		markup.row(*row3)
		bot.send_message(call.from_user.id,"Ожидайте...")
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
		#arendatory+='в размере: '
		#arendatory+="*"+str(summa_arendy)+" тг* в качестве аренды,"
		#arendatory+=" и *"+str(obw_dolg)+" тг* в качестве задолженности,\nитого ожидается: *\n"+str(summa_arendy+obw_dolg)+" тенге*"
		arendatory+="В качестве аренды: *"+str(summa_arendy)+" тенге*\n"
		arendatory+="В качестве задолженности: *"+str(obw_dolg)+" тенге*\n"
		arendatory+="Итого ожидается: *"+str(summa_arendy+obw_dolg)+" тенге*"
		bot.send_message(call.from_user.id,"Ближайшие *7 дней* ожидается оплата от арендаторов:\n"+arendatory,parse_mode='MARKDOWN',reply_markup=markup)

	except Exception as e:
		bot.send_message(call.from_user.id,"process_ozhidanie step: "+str(e))





@bot.callback_query_handler(func=lambda call: call.data == '/podtverdit')
def process_podtverdit(call):
	try:
		db = SQLight(constants.db)
		approve_list=db.get_sobytie()
		if approve_list:
			markup = telebot.types.InlineKeyboardMarkup()
			for data in approve_list:
				#db.get_manager(data[1])
				#print (data)
				row1=[telebot.types.InlineKeyboardButton("Офис - "+data[3]+", Имя - "+data[4]+', Сумма - '+str(data[5])+"тг",callback_data="approve"+data[-1])]
				markup.row(*row1)
			row2=[telebot.types.InlineKeyboardButton("Назад в меню",callback_data="nazadmenu")]
			markup.row(*row2)	
			bot.edit_message_text("<b>Список оплат для подтверждения</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=markup)
		else:
			bot.edit_message_text("<b>Нет платежей для подтверждения</b>", call.from_user.id, call.message.message_id,parse_mode='HTML')
			menu_message(call.from_user.id)
	except Exception as e:
		bot.send_message(call.from_user.id,"process_podtverdit step: "+str(e))

@bot.callback_query_handler(func=lambda call: call.data[:7] == 'approve')
def process_approve_klient(call):
	try:
		db = SQLight(constants.db)
		data=call.data[7:]
		approve = Approve(data)
		chat_id=call.from_user.id
		approve_dict[chat_id] = approve
		markup = telebot.types.InlineKeyboardMarkup()
		row1=[telebot.types.InlineKeyboardButton("Назад в меню",callback_data="nazadmenu")]
		row2=[telebot.types.InlineKeyboardButton("Назад",callback_data="nazadnazad")]
		markup.row(*row1)
		markup.row(*row2)
		bot.edit_message_text("<b>Отправьте фото чека</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=markup)		
		return
	except Exception as e:
		bot.send_message(call.from_user.id,"process_podtverdit step: "+str(e))
















@bot.callback_query_handler(func=lambda call: call.data[:5] == 'nazad')
def process_arendator(call):
	try:
		state=call.data[5:]
		chat_id=call.from_user.id
		print (state)
		db=SQLight(constants.db)
		if state=='oplata':
			buttons=db.get_podezd()
			podezd_markup = telebot.types.InlineKeyboardMarkup()
			for button in buttons:
				if button=='подвал':
					row=[telebot.types.InlineKeyboardButton(button,callback_data="podezd"+button)]
				else:
					row=[telebot.types.InlineKeyboardButton(button+" подъезд",callback_data="podezd"+button)]
				podezd_markup.row(*row)
			podezd_markup.row(telebot.types.InlineKeyboardButton("Отменить",callback_data="nazadmenu"))
			bot.edit_message_text("<b>Выберите подъезд:</b>",call.from_user.id, call.message.message_id,reply_markup=podezd_markup,parse_mode='HTML')
		if state=='menu':
			menu_message(chat_id,call.message.message_id)
		if state=='podezd':
			oplata=oplata_dict[chat_id]
			buttons=db.get_ofis(oplata.podezd)
			ofis_markup = telebot.types.InlineKeyboardMarkup()
			for button in buttons:
				row=[telebot.types.InlineKeyboardButton(button+" офис",callback_data="ofis"+button)]
				ofis_markup.row(*row)
			ofis_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadoplata"))
			bot.edit_message_text("<b>Выберите номер офиса:</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=ofis_markup)
		if state=='ofis':
			oplata=oplata_dict[chat_id]
			buttons=db.get_arendator(oplata.podezd,oplata.ofis)
			arendator_markup = telebot.types.InlineKeyboardMarkup()
			for button in buttons:
				row=[telebot.types.InlineKeyboardButton(button,callback_data="arenda"+button)]
				arendator_markup.row(*row)
			arendator_markup.row(telebot.types.InlineKeyboardButton("Назад",callback_data="nazadpodezd"))
			msg=bot.edit_message_text("<b>Выберите арендатора:</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=arendator_markup)
		if state=='nazad':
			print("NAZADDDD")
			db = SQLight(constants.db)
			approve_list=db.get_sobytie()
			try:
				approve=approve_dict[chat_id]
				approve.data=None
				approve.photo=None
			except:
				print("ERROR APPROVE NOT FOUND")
			if approve_list:
				markup = telebot.types.InlineKeyboardMarkup()
				for data in approve_list:
					#db.get_manager(data[1])
					#print (data)
					row1=[telebot.types.InlineKeyboardButton("Офис - "+data[3]+", Имя - "+data[4]+', Сумма - '+str(data[5])+"тг",callback_data="approve"+data[-1])]
					markup.row(*row1)
				row2=[telebot.types.InlineKeyboardButton("Назад в меню",callback_data="nazadmenu")]
				markup.row(*row2)
				bot.edit_message_text("<b>Список оплат для подтверждения</b>", call.from_user.id, call.message.message_id,parse_mode='HTML',reply_markup=markup)
				
			else:
				bot.edit_message_text("<b>Нет платежей для подтверждения</b>", call.from_user.id, call.message.message_id,parse_mode='HTML')
				menu_message(call.from_user.id)
	except Exception as e:
		bot.send_message(call.from_user.id,"Process_arendator step: "+str(e))




@bot.message_handler(content_types=['photo'])
def get_photo(message):
	try:
		chat_id = message.from_user.id	
		approve = approve_dict[chat_id]
		if approve.data:
			file_id=message.photo[-1].file_id
			file_info = bot.get_file(file_id)
			bot.send_message(message.from_user.id,"Загружаю данные в Google Sheets! Ожидайте...")
			name=message.from_user.first_name
			t=Thread(target=upload_to_google_drive, args=(message.from_user.id,message.from_user.first_name,file_info.file_path))
			t.start()
			t.join()
		else:
			bot.send_message(message.from_user.id,"Сначала заполните данные о клиенте")	
	except Exception as e: 
		print (e)
		bot.send_message(message.from_user.id,"Сначала заполните данные о клиенте")
		bot.send_message(295091909,"Error,get photo : "+str(e)+" From:"+str(message.from_user.username))

@bot.message_handler(content_types=['document'])
def get_photo_doc(message):
	try:
		chat_id = message.from_user.id	
		approve = approve_dict[chat_id]
		if approve.data:
			if message.document.mime_type in 'image/jpegimage/png':
				file_id=message.document.file_id
				file_info = bot.get_file(file_id)
				bot.send_message(message.from_user.id,"Загружаю данные в Google Sheets! Ожидайте...")
				name=message.from_user.first_name
				t=Thread(target=upload_to_google_drive, args=(message.from_user.id,message.from_user.first_name,file_info.file_path))
				t.start()
				t.join()
		else:
			bot.send_message(message.from_user.id,"Сначала заполните данные о клиенте")	
	except Exception as e: 
		print (e)
		bot.send_message(message.from_user.id,"Сначала заполните данные о клиенте")
		bot.send_message(295091909,"Error,get doc : "+str(e)+" From:"+str(message.from_user.username))
		



def upload_to_google_drive(chat_id,name,file_path):
	try:
		approve = approve_dict[chat_id]
		db=SQLight(constants.db)
		current="%Y-%m-%d"
		info=db.get_info(approve.data)[0]
		print (info)
		r=requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(constants.token, file_path),stream=True)
		month_dict={"01":"Январь","02":"Февраль","03":"Март","04":"Апрель","05":"Май","06":"Июнь","07":"Июль","08":"Август","09":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
		letter_dict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"AA",27:"AB",28:"AC",29:"AD",30:"AE"}

		file = name+'-'+info[3]+'-'+info[4]+'-'+str(info[5])+'-'+info[6]+'-'+'.jpg'
		f=open(file, 'wb')
		f.write(r.content)
			
		gauth = GoogleAuth(constants.client_secrets)
		# Try to load saved client credentials
		gauth.LoadCredentialsFile(constants.creds)
		if gauth.credentials is None:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
		elif gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
		else:
			# Initialize the saved creds
			gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile(constants.creds)
		drive = GoogleDrive(gauth)
		file2 = drive.CreateFile()
		file2.SetContentFile(file)
		file2.Upload()
		print('Created file %s with mimeType %s with id %s' % (file2['title'],
		file2['mimeType'],file2['id']))
		permission = file2.InsertPermission({
							'type': 'anyone',
							'value': 'anyone',
							'role': 'reader'})

		photo_path = file2['alternateLink']

		gc = pygsheets.authorize(service_file=constants.client,no_cache=True)
		try:
			sht = gc.open("список арендаторов")
		except Exception as e:
			print("CANT OPEN GOOGLE SHEET",e)
			sleep(30)
			sht = gc.open("список арендаторов")
		
		month_dict={"01":"Январь","02":"Февраль","03":"Март","04":"Апрель","05":"Май","06":"Июнь","07":"Июль","08":"Август","09":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
		letter_dict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"AA",27:"AB",28:"AC",29:"AD",30:"AE"}

		temp_time=info[-1].split('-')
		wsheet= month_dict[str(temp_time[1])]+" "+str(temp_time[0])			
		try:
			sheet = sht.worksheet('title',wsheet)
		except Exception as e:
			print("CANT OPEN GOOGLE WORKSHEET",e)
			sleep(30)
			sheet = sht.worksheet('title',wsheet)
		cell_list = sheet.find(info[-1])				
		print (info[-1])
		print (cell_list)
		
		temp_data=str(cell_list[0]).split(" ")[1]
		temp_end_index=temp_data.index("C")
		row_num=temp_data[1:temp_end_index]
		col_num=int(temp_data[temp_end_index+1:len(temp_data)])
		current="%Y-%m-%d %H:%M:%S"
		now_time=datetime.datetime.now()
		current_time = now_time.strftime(current)
		sheet.update_cell(letter_dict[int(col_num-1)]+str(row_num),name+": "+str(current_time))#doplata
		sheet.update_cell(letter_dict[col_num]+str(row_num),photo_path)#doplata
		menu_message(chat_id)
		db.delete_from_sobytie(info[-1])
		approve.data=None
		approve.phone=None
	except Exception as e:
		bot.send_message(chat_id,"Не смогли записать данные, сообщите @kirosoftware")
		bot.send_message(295091909,"upload: "+str(e))
	

















bot.remove_webhook()
bot.polling(True)