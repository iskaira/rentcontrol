#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

class SQLight:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
    def insert(self,podezd,ofis,arendator):
        with self.connection:
            return self.cursor.execute('INSERT INTO arendatory (podezd,ofis,arendator) values(?,?,?)',(podezd,ofis,arendator))
    def delete(self):
        with self.connection:
            return self.cursor.execute('DELETE FROM arendatory')

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
    
    def get_podezd(self):
        with self.connection:
            data=self.cursor.execute('SELECT distinct podezd from arendatory ORDER BY podezd').fetchall()
            print (data)
            data_list=[]
            for podezd in data:
                data_list.append(podezd[0])
            return data_list
            
    def get_ofis(self,podezd):
        with self.connection:
            data=self.cursor.execute('SELECT distinct ofis from arendatory where podezd=? ORDER BY ofis',(podezd,)).fetchall()
            print (data)
            data_list=[]
            for ofis in data:
                data_list.append(ofis[0])
            return data_list

    def get_arendator(self,podezd,ofis):
        with self.connection:
            data=self.cursor.execute('SELECT arendator from arendatory where podezd = ? and ofis= ? ',(podezd,ofis)).fetchall()
            data_list=[]
            print (data)
            for gorod in data:
                data_list.append(gorod[0])
            return data_list
    def add_sobytie(self,id,podezd,ofis,arendator,price,date):
        with self.connection:
            return self.cursor.execute('INSERT INTO sobytie (manager_id,podezd,ofis,arendator,price,date) values(?,?,?,?,?,?)',(id,podezd,ofis,arendator,price,date))
    def get_info(self,data):    
        with self.connection:
            return self.cursor.execute('SELECT * FROM sobytie where date=?',(data,)).fetchall()
    def get_sobytie(self):
        with self.connection:
            data=self.cursor.execute('SELECT * FROM sobytie').fetchall()
            if len(data)==0:
                return False
            return data

    def get_managers(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM managers').fetchall()

    def delete_from_sobytie(self,data):
        with self.connection:
            self.cursor.execute("DELETE FROM sobytie where date=?",(data,))
    def add_manager(self,id,name):
        with self.connection:
            return self.cursor.execute("INSERT INTO managers values(?,?)",(id,name))
    def remove_manager(self,id):
        with self.connection:
            return self.cursor.execute("DELETE FROM managers where id=? ",(id,))

            
#имя клиента, город, курсты
import constants
#import manager_db

if '__main__' == __name__:
    db=SQLight(constants.db)
    #print(db.add_sobytie(1,'aaa','aaa','aaa',522,'sa'))
    #print(db.add_manager(1,"VASYA"))
    #print(db.remove_manager(1))
    #print(db.get_managers())
    #db.doplata_num(77771000011)
    #print(db.get_manager(295091909))
    #print(db.del_manager(295091909))
    #print(db.get_kursy())
    #print(db.check_gorod_exist("ПМ"))
    #print(db.delete_kurs_city_tm("ТМ","Алматы",12))
'''
sqlite> create table sobytie(
   ...> row_id int primary key,
   ...> manager_id int,
   ...> podezd,
   ...> ofis,
   ...> arendator,
   ...> price,
   ...> date text
   ...> );

'''