#!/usr/local/bin/python2.7
# encoding: utf-8
import threading
from lib.db import Database
from lib.zombie import sina_zombie
#from lib.zombie import sohu_zombie
import datetime

import random
threadnum = 20
BASE = '/root/necromancer/'
DBPATH = BASE + 'db/zombie.sqlite'
FLAGPATH = BASE + 'flag.conf'
IPPATH = BASE + 'ip_list.csv'

flag = int(open(FLAGPATH,'r').read())
IP_LIST = open(IPPATH,'r').read().split('\n')

def now():
	return datetime.datetime.now()

def zombie_follow(zombie_id,zombie,st,db):
	target = db.get_follow_target(zombie_id)
	if zombie.follow(target[0],st):
		db.log_follow(zombie_id,target[1])
		return target[0]

def zombie_speak(zombie_id,zombie,db):
	speech = db.say_speech(zombie_id)
	if zombie.say(speech[0]):
		db.log_speech(zombie_id,speech[1])
		return speech[0]

# This is the zombie routine
def zombie_routine(zb,u_name,u_pass,u_id,db):
	if zb.login(u_name,u_pass):print 'logged in...'
	db.update_user(u_id,'suid',zb.get_suid())
	st = zb.get_st()
	print 'Followed: %s' % zombie_follow(u_id,zb,st,db)
	zb.home()
	print 'Spoke: %s' % zombie_speak(u_id,zb,db)
	# 1 means speak
	db.insert_move(u_id,now(),1)
	#zb.home()
	#age = zb.settings('birth')
	#db.update_user(u_id,'age',age)
	#print age
	#company = zb.settings('company')[0]
	#zb.home()
	#school = zb.settings('school')[0]
	#zb.home()
	#if random.randint(1,5) == 3:
	print 'Followed: %s' % zombie_follow(u_id,zb,st,db)
	db.update_user(u_id,'last_move',now())
	# 0 means follow
	#	print 'Followed: %s' % zb.follow(1951447215,st)

class Thread_Zombie(threading.Thread):
	"""docstring for ClassName"""
	def prepare(self,IP):
		self.db = Database(DBPATH)
		self.ip = IP
		self.zombie = sina_zombie(IP)
		zombie_info = self.db.get_zombie(0,1,now())[0]
		self.upass = zombie_info[2].strip('\r').strip('\n')
		self.uname = zombie_info[1]
		self.uid = zombie_info[0]
	def run(self):
		zombie_routine(self.zombie,self.uname,self.upass,self.uid,self.db)
		print self.ip,self.uname,self.upass,self.uid

for IP in IP_LIST[flag:flag+threadnum]:
	TZ = Thread_Zombie()
	TZ.prepare(IP)
	TZ.start()

if flag > 506:
	flag=0
else:
	flag += threadnum

print flag

f = open(FLAGPATH,'w')
f.write(str(flag))
f.close()

#This is a sohu zombie
# for ip in ip_list:
# 	zb = sohu_zombie(IP)
# 	zb.login('shao7007@sohu.com','web0909')
# 	zb.change_pass('web0909')
