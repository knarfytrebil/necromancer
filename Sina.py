from lib.SinaZombie import Zombie
import time
z = Zombie('aa','http://weibo.com')
z.login('knarfytrebil@gmail.com','ododlaed')
time.sleep(10)

z.br.render('google.png')
print "Screenshot written to 'google.png'"
