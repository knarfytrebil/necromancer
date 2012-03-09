#!usr/bin/python2.6
# encoding: utf-8

import sqlite3
import random

class Database:
	"""docstring for Database"""
	def __init__(self, db_path):
		self.db_path = db_path
	
	def connect(self):
		self.conn = sqlite3.connect(self.db_path)
		self.conn.text_factory = str
		return self.conn.cursor()
	
	def get_speech(self,speech):
		c = self.connect()
		SQL = 'SELECT id FROM main.speech WHERE sentence = ?'
		PARA = (speech,)
		c.execute(SQL,PARA)
		return c.fetchone()
	
	def get_label(self,label):
		c = self.connect()
		SQL = 'SELECT id FROM main.label WHERE name = ?'
		PARA = (label,)
		c.execute(SQL,PARA)
		return c.fetchone()
	
	def get_speech_his(self,uid):
		c = self.connect()
		SQL = 'SELECT speech FROM main.speech_log WHERE account = ?'
		PARA = (uid,)
		c.execute(SQL,PARA)
		his = []
		results = c.fetchall()
		for ids in results:
			his.append(ids[0])
		return his
	
	def gsb_id(self,sid):
		c = self.connect()
		SQL = 'SELECT sentence FROM main.speech WHERE id = ?'
		PARA = (sid,)
		c.execute(SQL,PARA)
		return c.fetchone()[0]

	def new_label_id(self):
		c = self.connect()
		SQL = 'SELECT id FROM main.label ORDER BY id DESC LIMIT 1'
		c.execute(SQL)
		return int(c.fetchone()) + 1
	
	def new_speech_id(self):
		c = self.connect()
		SQL = 'SELECT id FROM main.speech ORDER BY id DESC LIMIT 1'
		c.execute(SQL)
		result = c.fetchone()[0]
		if result == None:
			return 0
		else:
			return int(result) + 1
	
	def new_account_id(self):
		c = self.connect()
		SQL = 'SELECT id FROM main.account ORDER BY id DESC LIMIT 1'
		c.execute(SQL)
		result = c.fetchone()
		if result == None:
			return 0
		else:
			return int(result[0]) + 1
	
	def insert_label(self,lid,name):
		c = self.connect()
		SQL = 'INSERT INTO main.label (id,name) VALUES (?,?)'
		PARA = (lid,name)
		c.execute(SQL,PARA)
		self.conn.commit()
	
	def insert_speech(self,sid,words,label,tm):
		c = self.connect()
		SQL = 'INSERT INTO main.speech (id,sentence,label,time) VALUES (?,?,?,?)'
		PARA = (sid,words,label,tm)
		c.execute(SQL,PARA)
		self.conn.commit()

	def insert_account(self,aid,name,passwd,atype):
		c = self.connect()
		SQL = 'INSERT INTO main.account (id,type,password,gender,age,nick,follower,following,daily_follow,daily_speech,name) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
		PARA = (aid,atype,passwd,0,0,'UNKNOWN',0,0,0,0,name)
		c.execute(SQL,PARA)
		self.conn.commit()

	def ImportSpeech(self,speech_dir):
		import os
		file_list = os.listdir(speech_dir)
		for f in file_list:
			if f[0] != '.':
				label_name = f.split('.')[0]
				print label_name
				filetype = f.split('.')[1]
				label_id = self.get_label(label_name)[0]
				if label_id == None:
					self.insert_label(self.new_label_id(),label_name)
				label_file = open(speech_dir+label_name+'.'+filetype,'r')
				speeches = label_file.read().split('\n')
				for speech in speeches:
					if speech != '':
						if self.get_speech(speech) == None:
							self.insert_speech(self.new_speech_id(),speech,label_id,0)
				label_file.close()

	def ImportAccount(self,account_file):
		account_file = open(account_file,'r')
		atype = input("""What is the type?sina:0|sohu:1|163:2|qq:4""")
		accounts = account_file.read().split('\n')
		for account in accounts:
			account_name = account.split(',')[0]
			account_pass = account.split(',')[1]
			self.insert_account(self.new_account_id(),account_name,account_pass,atype)
	
	def say_speech(self,uid):
		speech_list = range(1,self.new_speech_id() - 1)
		speech_his = self.get_speech_his(uid)
		ran_pool = list(set(speech_list) - set(speech_his))
		sid = random.choice(ran_pool)
		speech = self.gsb_id(sid)
		return (speech,sid)
	
	def log_speech(self,uid,speech_id):
		c = self.connect()
		SQL = 'INSERT INTO main.speech_log (account,speech) VALUES (?,?)'
		PARA = (uid,speech_id)
		c.execute(SQL,PARA)
		self.conn.commit()
		SQL = 'UPDATE main.account SET daily_speech = daily_speech + 1 WHERE id = ?'
		PARA = (uid,)
		c.execute(SQL,PARA)
		self.conn.commit()
	
	def log_follow(self,uid,target_id):
		c = self.connect()
		SQL = 'INSERT INTO main.follow_log (account,followed_id) VALUES (?,?)'
		PARA = (uid,target_id)
		c.execute(SQL,PARA)
		self.conn.commit()
		SQL = 'UPDATE main.account SET daily_follow = daily_follow + 1 WHERE id = ?'
		PARA = (uid,)
		c.execute(SQL,PARA)
		self.conn.commit()
	
	def update_user(self,uid,key,value):
		c = self.connect()
		SQL = 'UPDATE main.account SET %s = ? WHERE id = ?' % key
		PARA = (value,uid)
		c.execute(SQL,PARA)
		self.conn.commit()
	
	def get_follow_target(self,uid):
		c = self.connect()
		SQL = 'SELECT id FROM main.account WHERE suid != 0 AND suid != 1'
		c.execute(SQL)
		results = c.fetchall()
		follow_list = []
		for ids in results:
			follow_list.append(ids[0])
		SQL = 'SELECT followed_id FROM main.follow_log WHERE account = ?'
		PARA = (uid,)
		c.execute(SQL,PARA)
		results = c.fetchall()
		followed_list= []
		for ids in results:
			followed_list.append(ids[0])
		rand_pool = list(set(follow_list) - set(followed_list)- set([uid]))
		if rand_pool == []:
			return (0,0)
		follow_target = random.choice(rand_pool)
		SQL = 'SELECT suid FROM main.account WHERE id = ?'
		PARA = (follow_target,)
		c.execute(SQL,PARA)
		target = c.fetchone()[0]
		return (target,follow_target)
	
	def insert_move(self,uid,mtime,mtype):
		c = self.connect()
		SQL = 'INSERT INTO main.moves (id,mtime,type) VALUES (?,?,?)'
		PARA = (uid,mtime,mtype)
		c.execute(SQL,PARA)
		self.conn.commit()

	def get_zombie(self,kind,num,last_move):
		c = self.connect()
		SQL = 'SELECT id,name,password FROM main.account WHERE suid != 0 AND last_move < ? AND type = ? LIMIT ?'
		from datetime import timedelta
		lmove = last_move - timedelta(hours=5)
		PARA = (lmove,kind,num)
		c.execute(SQL,PARA)
		results = c.fetchall()
		for i in results:
			self.update_user(i[0],'suid',0)
		return results