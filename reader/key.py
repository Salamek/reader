#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       key.py
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
import os
class virtkeys():
    
    enter = '{ENTER}'; #enter code
    
    def __init__(self):
        self.os_type = os.name
        self.keyapi = None
        if self.os_type == 'posix':#UNIX
            try:
                import virtkey
                self.keyapi = virtkey.virtkey()
            except ImportError: 
                raise Exception('Module virtkey is not installed, virtual keyboard feature will be disabled!')
            
        if self.os_type == 'nt': #WINDOWS
            try:
                import SendKeys
                self.keyapi = SendKeys
            except ImportError: 
                raise Exception('Module SendKeys is not installed, virtual keyboard feature will be disabled!')




    def press(self, keyname):
        if self.os_type == 'posix':#WINDOWS
            #enter hax

            if keyname.find(self.enter)>0:
                keyname = keyname.replace(self.enter,' ')
                send_special = 36
                
            if self.keyapi:
                for k in keyname:
                    self.keyapi.press_unicode(ord(k))
                    self.keyapi.release_unicode(ord(k))
                    
                if send_special:
                    self.keyapi.press_keycode(send_special)
                    self.keyapi.release_keycode(send_special)
                
        elif self.os_type == 'nt': #WINDOWS
            #enter hax
            keyname = keyname.replace(self.enter,'~')
            for k in keyname:
                #space hax
                k = k.replace(' ','{SPACE}')
                self.keyapi.SendKeys(k)

