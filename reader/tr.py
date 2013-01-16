import threading
import time



class TestThread(threading.Thread):#

	true = True
	def run(self):
		while self.true:
			print 'Patient: Doctor, am I going to die?'
			
	def stopo(self):
		self.true = False
		
	def starto(self):
		self.true = True
		
	

class AnotherThread():#threading.Thread
	#def run(self):
	def ss(self):
		cnt = 0
		while True:
			cnt = cnt + 1
			print '22222'
			if cnt > 10:
				break




dying = TestThread()

dying.start()
if dying.isAlive():
	print 'Doctor: No.'
else:
	print 'Doctor: Next!'

dying.stopo()
dying.starto()
print 'started and stopped'
dying.stopo()


living = AnotherThread()
living.ss()
#living.start()
#if living.isAlive():
#	print 'Doctor: No.'
#else:
#	print 'Doctor: Next!'