#!usr/bin/python2.6
# encoding: utf-8
import lib.handler as BrowserFactory
import time
import datetime
import urllib
from BeautifulSoup import BeautifulStoneSoup as BSS
import random
import re

HOME_SINA = 'http://weibo.cn'
HOME_SOHU = 'http://w.sohu.com'
LOGIN_TXT = '登录'
SETTING_TXT = '设置'
SOHU_SEND_TXT = '发表'
BASE = 'http://3g.sina.com.cn/prog/wapsite/sso/'
FOLLOW_LINK = 'http://weibo.cn/dpool/ttt/attnDeal.php?st=%s&act=add&uid=%s'
SOHU_FOLLOW_LINK = 'http://w.sohu.com/t2/addfri.do?ownerId=%s&uid=%s'
HOME_LINK = 'http://weibo.cn/dpool/ttt/home.php?p=top'
LOGOUT_LINK = 'http://3g.sina.com.cn/prog/wapsite/sso/loginout.php'

class sina_zombie:
	"""docstring for Crawler"""
	def __init__(self, ip):
		BrowserFactory.ip_addr = ip
		self.br = BrowserFactory.BindableBrowser()
		self.current_page = None
		self.br.set_handle_equiv(True)
		self.br.set_handle_redirect(True)
		self.br.set_handle_referer(True)
		self.br.set_handle_robots(False)
		self.br.addheaders = [('User-agent','Mozilla/ 5.0(Linux;U;2.2.1;Zh_cn;Desire HD;480*800;)AppleWebKit/528.5  (KHTML) Version/3.1.2/UCWEB7.6.0.75/ 139/999')]
		self.abspath = ''
		self.passwd = ''
	
	def xml_submit(self,url,data):
		return BSS(self.br._mech_open(url, urllib.urlencode(data)).read())
	
	def rand_sleep(self):
		sec = random.randint(3,5)
		time.sleep(sec)

	def login(self,usr_name,passwd):
		self.passwd = passwd
		self.current_page = BSS(self.br.open(HOME_SINA).read())
		login_link = self.current_page('a',limit=1)[0]['href']
		self.current_page = BSS(self.br.open(login_link).read())
		submit_link = BASE + self.current_page.find('go')['href']
		data = {}
		for postfield in self.current_page.findAll('postfield'):
			if postfield['value'].encode('utf8','ignore') != '$(password)':
				data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
			else:
				data[str(postfield['name'])] = passwd
		data['remember'] = '1'
		data['mobile'] = usr_name
		self.current_page = self.xml_submit(submit_link,data)
		home_link = self.current_page.find('a')['href']
		self.current_page = BSS(self.br.open(home_link).read())
		self.rand_sleep()
		return 1
	
	def get_suid(self):
		suid = self.current_page.findAll(href=re.compile('uid='))[0]['href'].split('&')[0].split('=')[1]
		return int(suid)
	
	def get_st(self):
		st = self.current_page.findAll(href=re.compile('st='))[0]['href'].split('&')[0].split('=')[1]
		return st
	
	def settings(self,stype):
		BASE = 'http://weibo.cn/dpool/ttt/'
		"""stype: school, birth , company, tag, intro"""
		link = BASE + self.current_page.findAll(href=re.compile('setting'))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()
		BASE = 'http://weibo.cn'
		link = BASE + self.current_page.findAll(href=re.compile(stype))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()
		if stype == 'school':
			return self.set_school()

		elif stype == 'company':
			return self.set_company()
		
		elif stype == 'birth':
			return self.set_birth()
		
		elif stype == 'tag':
			pass
		
		elif stype == 'intro':
			pass
		
		print self.current_page
	
	def set_birth(self):
		BASE = 'http://weibo.cn'
		data = {}
		submit_link = BASE + self.current_page.findAll('go')[0]['href']
		for postfield in self.current_page.findAll('postfield'):
			data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['day'] = str(random.randint(1,30))
		data['year'] = str(random.randint(1975,1985))
		data['month'] = str(random.randint(1,12))
		self.current_page = self.xml_submit(submit_link,data)
		return datetime.datetime.now().year - int(data['year'])
	
	def set_school(self):
		BASE = 'http://weibo.cn'
		
		link = BASE + self.current_page.findAll(href=re.compile('subact=search'))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()
		
		link = BASE + self.current_page.findAll(href=re.compile('stype=1'))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()
		
		link = BASE + self.current_page.findAll(href=re.compile('provid=31'))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()

		link = BASE + random.choice(self.current_page.findAll(href=re.compile('scn=')))['href']
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()

		data = {}
		submit_link = BASE + self.current_page.findAll('go')[0]['href']
		for postfield in self.current_page.findAll('postfield'):
			data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		name = data['scname']
		data['scremark'] = ''
		start = random.randint(1995,2004)
		data['scstart'] = str(start)
		self.current_page = self.xml_submit(submit_link,data)
		if self.current_page.findAll(href=re.compile('subact=del')) != None:
			return (name,start)
		else:
			return (0)
	
	def set_company(self):
		BASE = 'http://weibo.cn'
		company_kw = ['有限','公司','集团','电子','外贸','上海','北京','银行']
		data = {}
		submit_link = BASE + self.current_page.findAll('go')[0]['href']
		for postfield in self.current_page.findAll('postfield'):
			data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['keyword'] = random.choice(company_kw)
		self.current_page = self.xml_submit(submit_link,data)
		self.rand_sleep()
		company = random.choice(self.current_page.findAll(href=re.compile('scn=')))
		link = BASE + company['href']
		name = company.text
		self.current_page = BSS(self.br.open(link).read())
		data = {}
		submit_link = BASE + self.current_page.findAll('go')[0]['href']
		for postfield in self.current_page.findAll('postfield'):
			data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['scremark'] = ''
		start = random.randint(2004,2011)
		end = random.randint(start,2011)
		data['scend'] = str(end)
		data['scstart'] = str(start)
		self.rand_sleep()
		self.current_page = self.xml_submit(submit_link,data)
		if self.current_page.findAll(href=re.compile('subact=del')) != None:
			return (name,start)
		else:
			return (0)

	def say(self,speech):
		data = {}
		for postfield in self.current_page.findAll('postfield'):
			if postfield['value'].encode('utf8','ignore') != '$(password)':
				data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
			else:
				data[str(postfield['name'])] = passwd
		BASE = 'http://weibo.cn/dpool/ttt/'
		submit_link = BASE + self.current_page.findAll('go')[0]['href']
		for postfield in self.current_page.findAll('go')[0].findAll('postfield'):
			data[str(postfield['name'])] = str(postfield['value'])
		data['content'] = speech
		self.current_page = self.xml_submit(submit_link,data)
		self.rand_sleep()
		return 1
	
	def follow(self,user_id,st):
		if user_id != 0:
			self.current_page = BSS(self.br.open(FOLLOW_LINK % (st,user_id)).read())
			self.rand_sleep()
			return 1

	def home(self):
		self.current_page = BSS(self.br.open(HOME_LINK).read())
		self.rand_sleep()

	def logout(self):
		self.br.open(LOGOUT_LINK)

class sohu_zombie:
	"""docstring for Crawler"""
	def __init__(self, ip):
		BrowserFactory.ip_addr = ip
		self.br = BrowserFactory.BindableBrowser()
		self.current_page = None
		self.br.set_handle_equiv(True)
		self.br.set_handle_redirect(True)
		self.br.set_handle_referer(True)
		self.br.set_handle_robots(False)
		self.br.addheaders = [('User-agent','Mozilla/ 5.0(Linux;U;2.2.1;Zh_cn;Desire HD;480*800;)AppleWebKit/528.5  (KHTML) Version/3.1.2/UCWEB7.6.0.75/ 139/999')]
		self.auid = ''
		self.apwd = ''
		self.abspath = ''
		self.owner_id = 0
		self.passwd = ''
	
	def xml_submit(self,url,data):
		return BSS(self.br._mech_open(url, urllib.urlencode(data)).read())
	
	def rand_sleep(self):
		sec = random.randint(10,20)
		time.sleep(sec)
		print('slept %s seconds....' % sec)

	def login(self,usr_name,passwd):
		self.passwd = passwd
		self.current_page = BSS(self.br.open(HOME_SOHU).read())
		login_link = HOME_SOHU + self.br.find_link(text_regex=re.compile(LOGIN_TXT)).url
		self.current_page = BSS(self.br.open(login_link).read())
		submit_link = HOME_SOHU + self.current_page.find('form')['action']
		data = {}
		for postfield in self.current_page.findAll('input'):
			if postfield['type'] not in ['button','submit']:
				data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['u'] = usr_name
		data['p'] = passwd
		data['fr'] = 'null'
		self.current_page = self.xml_submit(submit_link,data)
		self.rand_sleep()
	
	def say(self,speech):
		data = {}
		form_div = self.current_page.find('div',{'class':'t2'})
		for postfield in form_div.findAll('input'):
			if postfield['type'] not in ['button','submit']:
					data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['send'] = SOHU_SEND_TXT
		data['zturl'] = ''
		data['hiddenContent'] = ''
		data['content'] = speech
		data['kw'] = ''
		# BASE = 'http://weibo.cn/dpool/ttt/'
		submit_link = HOME_SOHU + form_div.find('form')['action']
		self.current_page = self.xml_submit(submit_link,data)
		print self.current_page
		self.rand_sleep()
	
	def follow(self,user_id):
		para = (self.owner_id,user_id)
		self.br.open(SOHU_FOLLOW_LINK % para)
		self.rand_sleep()

	def home(self):
		self.current_page = BSS(self.br.open(HOME_SOHU).read())
		self.rand_sleep()

	def logout(self):
		self.br.open(LOGOUT_LINK)

	def change_pass(self,passwd):
		data = {}
		link = HOME_SOHU + self.br.find_link(text_regex=re.compile(SETTING_TXT)).url
		self.current_page = BSS(self.br.open(link).read())
		self.rand_sleep()
		link = HOME_SOHU + self.current_page.findAll(href=re.compile('upass'))[0]['href']
		self.current_page = BSS(self.br.open(link).read())
		for postfield in self.current_page.findAll('input'):
			if postfield['type'] not in ['button','submit']:
					data[str(postfield['name'])] = postfield['value'].encode('utf8','ignore')
		data['password'] = self.passwd
		data['newpass'] = passwd
		# BASE = 'http://weibo.cn/dpool/ttt/'
		submit_link = HOME_SOHU + self.current_page.find('form')['action']
		self.current_page = self.xml_submit(submit_link,data)
		print self.current_page
		self.rand_sleep()
