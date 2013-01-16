#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       app.py
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


from ftplib import FTP
import os, hashlib, urllib2

class comit:
  mirror_list ='mirror.list'
  to_update = []
  url_ok = None
  md5sum = 'md5.sum'
  platform = 'windows'
  dir_to_send = None
  we_got_md5 = {}
  def __init__(self):
      version = raw_input("Enter version name 1.x and so or devel:").strip()
      self.dir_to_send = './' + version + '/dist/'
      self.to_upload()
      self.comit()

  def md5_for_file(self, file, block_size=2**20):
      f = open(file, 'rb')
      md5 = hashlib.md5()
      while True:
          data = f.read(block_size)
          if not data:
              break
          md5.update(data)
      return md5.hexdigest()

  def download(self, url, dest_name=False):
		con = urllib2.urlopen(url)
		data = con.read()
		if dest_name:
			local = open(dest_name, 'wb')
			local.write(data)
			local.close()
		return data

  def to_upload(self):
  		if os.path.exists(self.mirror_list):
  			urls = [line.strip() for line in open(self.mirror_list)]
  			print 'Using local ' + self.mirror_list
  		else: #default urls
  			urls = ['http://reader-update.sg1-game.net/']

  		for url in urls:
  			try:
  				print 'Downloading ' + self.mirror_list + '...'
  				self.download(url + self.mirror_list,self.mirror_list)
  				print 'Done!'
  				self.url_ok = url
  				break;
  			except:
  				print 'Connecion to ' + url + 'failed!'

  		if self.url_ok:
  			print 'Downloading ' + self.md5sum + '...'
  			try:
  				self.download(url + self.platform + '/' + self.md5sum, self.md5sum)
  				print 'Done!'
  				md5s = [line.strip() for line in open(self.md5sum)]
  				for md5file in md5s:
  				  tmp = md5file.split(' ')
  				  self.we_got_md5[tmp[0]] = tmp[1]
  			except:
  				self.we_got_md5 = False
  				print 'Failed, cannot continue!'


  def comit(self):
    tmp_file = 'md5.tmp'
    mirror_list ='mirror.list'
    if  os.path.exists(self.dir_to_send):
    	ftp = FTP('sg1-game.net')
    	ftp.login('login','password')
    	ftp.storbinary('STOR ' + mirror_list, open(mirror_list, 'rb'))
    	ftp.cwd('windows')
    	listing = os.listdir(self.dir_to_send)
    	print 'Creating sum file'
    	md5s = ''
    	for infile in listing:
    		if os.path.isfile(self.dir_to_send + infile):
    			md5s = md5s + infile + ' ' + self.md5_for_file(self.dir_to_send + infile) + "\n"

    	tmpf = open(tmp_file, 'wb')
    	tmpf.write(md5s)
    	tmpf.close()


    	for infile in listing:
			if os.path.isfile(self.dir_to_send + infile):
				if self.we_got_md5:
					if infile in self.we_got_md5:
						if self.we_got_md5[infile] != self.md5_for_file(self.dir_to_send + infile):
							print 'Uploading ' + infile
							ftp.storbinary('STOR ' + infile, open(self.dir_to_send + infile, 'rb'))
				else:
					if os.path.isfile(self.dir_to_send + infile):
						print 'Uploading ' + infile
						ftp.storbinary('STOR ' + infile, open(self.dir_to_send + infile, 'rb'))
    	ftp.storbinary('STOR md5.sum', open(tmp_file, 'rb'))
    	os.remove(tmp_file)
    	print 'Upload Finished!'
    	ftp.quit()
    else:
    	 raise Exception('Source destination not found!')


if __name__ == "__main__":
    comit = comit()
    #comit.to_upload()
    #comit.comit()
