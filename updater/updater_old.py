#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       updater.py
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

import os, hashlib
import urllib2
import threading

try:
    import gtk
except ImportError: 
    print 'GTK not found!, using terminal for output!'
    
    
#gtk threads init
gtk.gdk.threads_init()
    
    
    
class updater:
    
    update_dir = 'reader/'
    mirror_list ='mirror.list'
    platform = 'windows'
    md5sum = 'md5.sum'
    we_got_md5 = False
    url_ok = ''

    to_update = []
    gtk_dialog = False

    def __init__(self):
            #DO UPDATE ?
            #self.ask_label = gtk.Label("New updates found!")
            #self.ask = gtk.Dialog("Do you want perform updates now ?",
            #                    None,
            #                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            #                    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
            #                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            #self.ask.vbox.pack_start(self.ask_label)
            #self.ask_label.show()
            
            self.progressbar = gtk.ProgressBar()
            
            self.update_win = gtk.Window()
            self.update_win.set_title("Doing update...")
            self.update_win.add(self.progressbar)
            
            
    #zaloguje a zobrazi ten balast
    def logger(self,message):
        print message
        #self.status_win_label = gtk.Label(message)
        #self.status_win = gtk.Dialog(message,
        #                   None,
        #                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        #self.status_win.vbox.pack_start(self.status_win_label)
        #self.status_win_label.show()
        #self.status_win.show()
        #response = self.status_win.run()
        #self.status_win.destroy()
    
    def md5_for_file(self, file, block_size=2**20):
        f = open(file, 'rb')
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        ret = md5.hexdigest()
        f.close()
        return ret

    def download(self, url, dest_name=False):
        con = urllib2.urlopen(url)
        data = con.read()
        if dest_name:
            local = open(dest_name, 'wb')
            local.write(data)
            local.close()
        return data
        
        
    #run my app
    def run(self):
        if os.name == 'nt':
            to_run = self.update_dir + 'reader.exe'
            if os.path.isfile(to_run):
                print 'Lets run it !'
                os.system('"%s"' % os.path.abspath(to_run))
            else:
                self.logger('Executable not found, lets wait 10s and try it again!')
                self.update()

    def update(self):
        if os.path.exists(self.update_dir):
                print 'Dir ok'
        else:
                os.mkdir(self.update_dir)
                print 'Creating directory'
        if os.path.exists(self.mirror_list):
            urls = [line.strip() for line in open(self.mirror_list)]
            self.logger('Using local ' + self.mirror_list)
        else: #default urls
            urls = ['http://reader-update.sg1-game.net/']

        for url in urls:
            try:
                self.logger('Downloading ' + self.mirror_list + '...')
                self.download(url + self.mirror_list,self.mirror_list)
                print 'Done!'
                self.url_ok = url
                break;
            except:
                self.logger('Connecion to ' + url + 'failed!')

        if self.url_ok:
            self.logger('Downloading ' + self.md5sum + '...') 
            try:
                self.download(self.url_ok + self.platform + '/' + self.md5sum, self.update_dir + self.md5sum)
                print 'Done!'
                self.we_got_md5 = True
            except:
                self.we_got_md5 = False
                self.logger('Failed, cannot continue!')

            if self.we_got_md5: 
                md5s = [line.strip() for line in open(self.update_dir + self.md5sum)]
                for md5file in md5s:
                    splited = md5file.split(' ')
                    if os.path.exists(self.update_dir + splited[0]):
                        curmd5 = self.md5_for_file(self.update_dir + splited[0])
                        if splited[1]!= curmd5:
                            self.to_update.append(splited[0])
                    else:
                        self.to_update.append(splited[0])
                
                if len(self.to_update) > 0 :
                    response = gtk.RESPONSE_ACCEPT
                    #response = self.ask.run()
                    if gtk.RESPONSE_REJECT == response:
                        print 'Update Canceled!'
                        #self.ask.destroy()
                        self.run()
                    elif gtk.RESPONSE_ACCEPT == response:
                        #self.ask.destroy()
                        self.logger('Doing update!')
                        self.update = update(self)
                        self.update.start()
                        self.update_win.show_all()
                        #for update in self.to_update:
                        #    self.logger('Updating file ' + update)
                        #    self.download(url + self.platform + '/' + update, self.update_dir + update)
                        #    print 'Done!'
                else:
                    self.logger('All files are up to date!')
                    self.run()

    def main(self):
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()


class update(threading.Thread):
    
    def __init__(self, updater):
        threading.Thread.__init__ (self)
        self.updater = updater
        
        
    def run(self):
         for update in self.updater.to_update:
            print 'Updating file ' + update
            self.updater.progressbar.set_text(update)
            self.updater.download(self.updater.url_ok + self.updater.platform + '/' + update, self.updater.update_dir + update)
         print 'Update Completed!'
         self.updater.run()
            
    def stop(self):
        self.stopthread.set()



if __name__ == "__main__":
    updater = updater()
    updater.update()
