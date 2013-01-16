#!/usr/bin/python
import threading
import gtk

import time
import os, hashlib
import urllib2

gtk.gdk.threads_init()

class updater(gtk.Window):
    
    update_dir = 'reader/'
    mirror_list ='mirror.list'
    platform = 'windows'
    md5sum = 'md5.sum'
    we_got_md5 = False
    url_ok = ''

    to_update = []

    def __init__(self, threads=None):
        super(updater, self).__init__()

        #self.ask_label = gtk.Label("New updates found!")
        #self.ask = gtk.Dialog("Do you want perform updates now ?",
        #                    None,
        #                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        #                    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
        #                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        #self.ask.vbox.pack_start(self.ask_label)
        #self.ask_label.show()



        self.connect("destroy", self.quit)
        self.set_title("Updating...")
        
        vbox = gtk.VBox(False, 4)
        
        self.pb = gtk.ProgressBar()
        vbox.pack_start(self.pb, False, False, 0)
        self.lb = gtk.Label("Update!")
        vbox.pack_start(self.lb, False, False, 0)
        
        #messs
        if os.path.exists(self.update_dir):
                self.logger('Dir ' + self.update_dir + ' is ok')
        else:
                os.mkdir(self.update_dir)
                self.logger('Creating directory ' + self.update_dir)
        if os.path.exists(self.mirror_list):
            urls = [line.strip() for line in open(self.mirror_list)]
            self.logger('Using local ' + self.mirror_list)
        else: #default urls
            urls = ['http://reader-update.sg1-game.net/']

        for url in urls:
            #trying repositories
            try:
                self.logger('Downloading ' + self.mirror_list + '...')
                self.download(url + self.mirror_list,self.mirror_list)
                self.logger(self.mirror_list + ' Done!')
                self.url_ok = url
                break;
            except:
                self.logger('Connecion to ' + url + 'failed!')
        
        #we found working server, we can continue !
        if self.url_ok:
            self.logger('Downloading ' + self.md5sum + '...') 
            #try download md5 sum list
            try:
                self.download(self.url_ok + self.platform + '/' + self.md5sum, self.update_dir + self.md5sum)
                self.logger(self.md5sum + ' Done!')
                self.we_got_md5 = True
            except:
                self.we_got_md5 = False
                self.logger('Failed, cannot continue!')

            #if we got MD5 sum list we can continue !
            if self.we_got_md5: 
                #parsing md5sum file AND checking for new files 
                md5s = [line.strip() for line in open(self.update_dir + self.md5sum)]
                for md5file in md5s:
                    splited = md5file.split(' ')
                    if os.path.exists(self.update_dir + splited[0]):
                        curmd5 = self.md5_for_file(self.update_dir + splited[0])
                        if splited[1]!= curmd5:
                            self.to_update.append(splited[0])
                    else:
                        self.to_update.append(splited[0])
                
                #we got some files to update !
                if len(self.to_update) > 0 :
                    #response = gtk.RESPONSE_ACCEPT
                    response = self.ask.run()
                    if gtk.RESPONSE_REJECT == response:
                        print 'Update Canceled!'
                        self.ask.destroy()
                        #self.run()
                    elif gtk.RESPONSE_ACCEPT == response:
                        self.ask.destroy()
                        self.logger('Doing update!')
                        self.trhead = update(self) #how many files
                        self.trhead.start()
                        self.add(vbox)
                        self.show_all()
                else:
                    self.logger('All files are up to date!')
                    #self.run()

        
    def logger(self,message):
        print message
        
        
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
        
        
    def quit(self, obj = None):
        self.trhead.stop()
        gtk.main_quit()
        
class update(threading.Thread):
    def __init__(self, updater):
        threading.Thread.__init__ (self)
        self.updater = updater
        self.count = len(self.updater.to_update)
        self.step = 1/float(self.count)
        self.stopthread = threading.Event()

    def run(self):
        if not self.stopthread.isSet():
            cnt = 1
            for i in self.updater.to_update: 
                self.updater.download('http://reader-update.sg1-game.net/windows/' + i, 'reader/' + i)
                #progressbar 
                val = cnt * self.step
                cnt = cnt + 1
                self.updater.pb.set_fraction(val)
                self.updater.pb.set_text(str(int(val*100)) + '%')
                #self.pb.set_text('Updating: ' + str(cnt) + '/' + str(self.count))
                self.updater.lb.set_text('Updating: ' + i)
            self.updater.quit()
            
        
    def stop(self):
        print 'stopped'
        self.stopthread.set()
        
if __name__ == "__main__":
    updater = updater()
    
    
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
