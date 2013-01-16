#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       i18n.py
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

import ConfigParser
import os

class i18n:
	
	def __init__(self, language):
		self.lang = ConfigParser.RawConfigParser()
		self.cache = {}
		self.language = language
		self.set_file('languages.txt')
	
	def set_file(self, filename):
		if os.path.exists(filename)!=True:
		  filename = 'reader/' + filename 
		if os.path.exists(filename):
			self.lang.read(filename)
			try:
				translate_file = self.lang.items(self.language)
				for trns in translate_file:
					self.cache[trns[0]] = trns[1]
			except ConfigParser.NoSectionError:
				print 'Language ' + self.language + ' not found!'
				
		else:
			print 'File not found' 

	def translate(self, string):
		string = string.lower()
		if string in self.cache:
			return self.cache[string]
		else:
			return string
			
	def languages(self):
		return self.lang.sections()
