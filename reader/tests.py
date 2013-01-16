#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       tests.py
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

#print acr122l.LCD_back_light(True)
#print acr122l.LED_control('0101')

#print acr122l.LCD_Clear()
#print acr122l.LCD_Text(False,'A',0x00,'AHA!')
#print acr122l.LCD_Text(False,'A',0x00,'')
#print acr122l.LCD_Contrast(10)
#pixels = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
#pixels = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
#print acr122l.LCD_Graphic(False,0x05,pixels)
#print acr122l.LCD_Scrolling() # dodelat buguje se
#print acr122l.Buzzer_control(1,1,1)#opravit, ma specialni odpoved
#print acr122l.Buzzer_Led_control('00000001',1, 1, 1,'on') #opravit, ma specialni odpoved
#print acr122l.get_sam_version(1) #opravit, ma specialni odpoved
#TAG CONTROL
#first we must decrypt card
print acr122l.TAG_Authenticate(0x00, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
#reads value from block 0x01
#print acr122l.TAG_Read(0x01)
#data = [0x44,0x72,0x61,0x63,0x75,0x6c,0x65] #dracule in HEX
#data = '8595505110110'
#print acr122l.TAG_Update(0x01,data,'ASCII')

