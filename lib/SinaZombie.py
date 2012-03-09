#!usr/bin/python2.6
# encoding: utf-8

"""
A Wonderful Zombie for SinaWeibo
"""

from Core.WebkitZombie import base

class Zombie(base):
	"""docstring for ClassName"""
	def login(self,usr,passwd):
		return self._login('#login_submit_btn',loginname=usr,password=passwd,password_text=passwd)

	def logout(self):
		self.br.at_xpath('//*[@nodetype="exit"]').click()