#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       poling.py
#       
#       Copyright 2011 Adam Schubert <feartohell@seznam.cz>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


from acr122l import acr122l

acr122l = acr122l()
#**********
#POLING APP
#**********

cnt = 1
while True:
	ret = acr122l.TAG_Polling()

	if ret:
		if cnt != ret[17]:
			cnt = ret[17]
			target_number = ret[18] #Target number 
			sens_res = [ret[19],ret[20]] #SENS_RES  
			sel_res = ret[21] #SEL_RES  
			len_uid = ret[22] #Length of the UID 
			end_uid = 23+len_uid
			uid = []
			
			for i in range(23, end_uid):
				uid.append(i)
				
			ats = []
			for a in range(end_uid,end_uid+7):
				ats.append(a)
				
			print acr122l.LCD_Clear()
			print acr122l.LCD_back_light(True)
			print acr122l.LCD_Text(False,'A',0x00,acr122l.tag_type(sel_res) + ' tags detected')
			#print acr122l.Buzzer_control(1,1,1)
	else:
		if cnt:
			cnt = 0
			print acr122l.LCD_Clear()
			print acr122l.LCD_back_light(False)
			print acr122l.LCD_Text(False,'A',0x00,'Waiting for tag!')

		
