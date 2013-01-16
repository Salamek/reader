from acr122l import acr122l
import time
acr122l = acr122l()
true = True
def read_card():
	global true
	true = False

	key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
	print acr122l.TAG_Authenticate(0x00, key)
	print 'Starting read data'
	readed = acr122l.TAG_Read(0x01)
	if readed:
		acr122l.LCD_Clear()
		acr122l.LED_control('0010')
		acr122l.LCD_Text(False,'A',0x00,'Done! Wait 10 s to next scan...')
		acr122l.LCD_Text(False,'A',0x40,readed)
		acr122l.Buzzer_control(1,1,1)
	else:
		acr122l.LCD_Clear()
		acr122l.LED_control('0001')
		acr122l.LCD_Text(False,'A',0x00,'Error,Scan again')
		acr122l.LCD_Text(False,'A',0x40,'Wait 10 s to next scan...')
		acr122l.Buzzer_control(10,10,1)
		
	time.sleep(5)
	acr122l.LCD_back_light(True)
	acr122l.LED_control('1000')
	true = True
	acr122l.LCD_Clear()
	acr122l.LCD_Text(False,'A',0x00,'Ready')


#cnt = 1
acr122l.LED_control('1000')
acr122l.LCD_back_light(True)
acr122l.LCD_Clear()
acr122l.LCD_Text(False,'A',0x00,'Ready')

while true:
	ret = acr122l.TAG_Polling()

	if ret:
		acr122l.LCD_Clear()
		acr122l.LCD_Text(False,'A',0x00,'Reading...')
		acr122l.LED_control('0100')
		#if cnt != ret[17]:
			#cnt = ret[17]
		target_number = ret[18] #Target number 
		sens_res = [ret[19],ret[20]] #SENS_RES  
		sel_res = ret[21] #SEL_RES  
		len_uid = ret[22] #Length of the UID 
		end_uid = 25+len_uid
		uid = []
		for i in range(25, end_uid):
			uid.append(ret[i])
		
		if uid:
			read_card()
			#break
		#else:
		#	true = False


	#else:
	#	if cnt:
	#		cnt = 0




 
