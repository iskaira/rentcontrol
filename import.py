import telebot
import constants
import requests
import pygsheets
from datetime import datetime
from pytz import timezone
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from manager_db import SQLight
from os import system
from time import sleep
db=SQLight(constants.db)
bot = telebot.TeleBot(constants.token)
for i in range(3):
	ok=0
	file=''
	data=db.get_last_row_import()
	if len(data)>0:
		fmt = "%Y-%m-%d %H:%M:%S"
		time_zone='Asia/Almaty'
		current="%Y-%m-%d"
		now_time = datetime.now(timezone(time_zone))
		current_time = now_time.strftime(current)
		now_current_time= now_time.strftime(fmt)
		print (data)
		data=data[0]
		row_id=data[0]
		id=data[1]
		m_name=data[2]
		m_surname=data[3]
		m_username=data[4]
		date =data[5]
		phone =data[6]
		name =data[7]
		course =data[8]
		email =data[9]
		city =data[10]
		potok =data[11]
		price =data[12]
		fact_price =data[13]
		doplata =data[14]
		file_path =data[15]
		r=requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(constants.token, file_path),stream=True)
		month_dict={"01":"Январь","02":"Февраль","03":"Март","04":"Апрель","05":"Май","06":"Июнь","07":"Июль","08":"Август","09":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
		letter_dict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"AA",27:"AB",28:"AC",29:"AD",30:"AE"}

		file = m_name+m_surname+'-'+str(phone)+'.jpg'
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
			sht = gc.open("TF")
			sheet = sht.worksheet('title','События')
		except Exception as e:
			bot.send_message(295091909,"ТФ sheet OPEN:"+str(e))
			
		index = 1


		manager_name=db.get_manager(id)
		manager=gc.open(manager_name)

		#####################################################################################
		#####################################################################################


		if doplata is None:		
			month=month_dict[date.split("-")[1]]
			print(month)
			print(manager_name)
			try:
				manager_sheet = manager.worksheet('title',month)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"менеджер sheet OPEN:"+str(e))
			try:
				kurs_gs=gc.open(course)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"kurs sheet OPEN:"+str(e))
			if city is None:
				temp_title=course+" "+str(potok)
			else:
				temp_title=city+" "+course+" "+str(potok)
			try:
				kurs_sheet=kurs_gs.worksheet('title',temp_title)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"kurs sheet, kurs imya proverit nado KURS OPEN: "+str(e))
			
			row = [date,manager_name,name,phone,email,city,course,potok,price,fact_price,doplata,photo_path,now_current_time]
			
			try:
				sheet.insert_rows(index,values=row)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"insert_row Sobytie OPEN:"+str(e))
			
			
			if city is None:
				row_manager = [manager_name,name,phone,str(course)+" "+str(potok),price,"","",fact_price,"","","","","",photo_path,"","","","","",date,"","","","","",current_time]
				row_kurs = [manager_name,name,phone,str(course)+" "+str(potok),price,"","",fact_price,"","","","","",email]
			else:
				row_manager = [manager_name,name,phone,str(city)+" "+str(course)+" "+str(potok),price,"","",fact_price,"","","","","",photo_path,"","","","","",date,"","","","","",current_time]
				row_kurs = [manager_name,name,phone,str(city)+" "+str(course)+" "+str(potok),price,"","",fact_price,"","","","","",email]
			try:
				manager_sheet.insert_rows(index,values=row_manager)
				kurs_sheet.insert_rows(index,values=row_kurs)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"insert_to manager and kurs: "+str(e))

		else:
			client_info=db.get_client_info(phone)
			month=month_dict[(str(client_info[-1]).split("-")[1])]
			kurs=client_info[2]
			gorod=client_info[1]
			potok=client_info[3]
			print(month)
			print(manager_name)
			try:
				manager_sheet = manager.worksheet('title',month)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"Manager_sheet title Doplata WORKSHEET: "+str(e))
			
			print (client_info)
			
			if client_info[1] is None or client_info[1] is '':
				temp_title=client_info[2]+" "+str(client_info[3])
			else:
				temp_title=client_info[1]+" "+client_info[2]+" "+str(client_info[3])
			try:
				kurs_gs=gc.open(client_info[2])
				kurs_sheet=kurs_gs.worksheet('title',temp_title)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"kurs open worksheet: "+temp_title+str(e))
			try:
				cell_list = manager_sheet.find(phone)
				cell_list_kurs = kurs_sheet.find(phone)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"CELL FIND: "+str(e))
			
			temp_data=str(cell_list[0]).split(" ")[1]
			temp_end_index=temp_data.index("C")
			row_num=temp_data[1:temp_end_index]
			
			row_from_manager=manager_sheet.get_row(row_num)
			dpl=1
			for i in range(8,13):
				if row_from_manager[i]=='':
					dpl=i-7
					print(dpl)
					if dpl>5:
						dpl=5
					break



			try:
				manager_sheet.update_cell(letter_dict[7+dpl]+str(row_num),str(doplata))#doplata1
				manager_sheet.update_cell(letter_dict[13+dpl]+str(row_num),str(photo_path))#checkdop1
				manager_sheet.update_cell(letter_dict[19+dpl]+str(row_num),str(date))#datadop1
				manager_sheet.update_cell(letter_dict[25+dpl]+str(row_num),str(current_time))
				temp_data=str(cell_list_kurs[0]).split(" ")[1]
				temp_end_index=temp_data.index("C")
				row_num=temp_data[1:temp_end_index]
				kurs_sheet.update_cell(letter_dict[7+dpl]+str(row_num),str(doplata))#doplata1
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"UPDate in doplata: "+str(e))

			#('Oskar', 'Almaty', 'A', '42', 'kiro@gmail.com', 45000)
			try:
				if client_info:
					row = [date,manager_name,client_info[0],phone,client_info[4],client_info[1],client_info[2],client_info[3],client_info[5],fact_price,doplata,photo_path,now_current_time]
					sheet.insert_rows(index,values=row)
				else:
					row = [date,manager_name,name,phone,email,city,course,potok,price,fact_price,doplata,photo_path,now_current_time]
					sheet.insert_rows(index,values=row)
				ok+=1
			except Exception as e:
				bot.send_message(295091909,"insert to sheet sobytie in DOPLATA: "+str(e))
			
		try:
			cell_list = manager_sheet.find(phone)
			cell_list_kurs = kurs_sheet.find(phone)
			temp_data=str(cell_list[0]).split(" ")[1]
			temp_end_index=temp_data.index("C")
			temp_end=temp_data[1:temp_end_index]	
			formula='H'+str(temp_end)+ "+" +'I'+str(temp_end)+ "+" +'J'+str(temp_end)+ "+" +'K'+str(temp_end)+ "+" +'L'+str(temp_end)+ "+" +'M'+str(temp_end)
			manager_sheet.update_cell('F'+str(temp_end),'='+formula)
			manager_sheet.update_cell('G'+str(temp_end),'=if('+'(E'+str(temp_end) + "-" +"F"+str(temp_end)+")>0,"+'E'+str(temp_end) + "-" +"F"+str(temp_end)+",0)")#dolg
			
			temp_data=str(cell_list_kurs[0]).split(" ")[1]
			temp_end_index=temp_data.index("C")
			temp_end=temp_data[1:temp_end_index]
			
			kurs_sheet.update_cell('F'+str(temp_end),'='+formula)#oplatil vsego
			#=if((E4-F4)>0,E4-F4,0)
			kurs_sheet.update_cell('G'+str(temp_end),'=if('+'(E'+str(temp_end) + "-" +"F"+str(temp_end)+")>0,"+'E'+str(temp_end) + "-" +"F"+str(temp_end)+",0)")#dolg
			
		except Exception as e:
			bot.send_message(295091909,"FORMULA OBWAYA: "+str(e))
		############################################################################################################
	print("DEL")
	print(file)
	system('python del.py root/'+file)
	print("Happened")
	if ok==5:
		db.delete_data()
	else:
		bot.send_message(295091909,"NOT OK: ")
	sleep(17)