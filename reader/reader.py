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


#Depends:
#python-virtkey - Linux
#python-sendkeys - Windows
#Pexpect

#importing PyGTK
import pygtk
pygtk.require('2.0')

#importing GTK+
import gtk

#importing acr122l lib
from acr122l import acr122l

#importing i18n lib
from i18n import i18n

#importing config parser
import ConfigParser

#importing os
import os

#importing time
import time

#import trhead
import threading

#import virtual keyboard
from key import virtkeys

#import json
import json

from single import SingleInstance


#gtk threads init
gtk.gdk.threads_init()

#*********************************************************************************************************
#class poolcard
#*********************************************************************************************************
class poolcard(threading.Thread):
    def __init__(self, acr122l, reader):
        self.acr122l = acr122l
        self.reader = reader
        threading.Thread.__init__ (self)


    def run(self):
        self.stopthread = threading.Event()

        while not self.stopthread.isSet():
            ret = self.acr122l.TAG_Polling()
            if ret:
                self.reader.lcd_states('reading')
                self.acr122l.LED_control('0100')

                if ret['uid']:
                    self.reader.read_card(None,None,True)

    def stop(self):
        self.stopthread.set()

#*********************************************************************************************************
#Class reader
#*********************************************************************************************************
class reader ():


    #*************
    #Global values
    #*************
    first_run = False
    polt = None
    acr122l = None
    lcd_size = 16
    i18n = False
    available_ports = []
    languages = []
    icon = 'reader.ico'
    version = '1.4'
    
    available_baudrates = [9600,115200]


    home = os.getenv('HOME')
    if home == None:
        home = os.path.expanduser("~") 
    main_dir = home + '/.reader/'
    
    
    #new config default values
    device = {'language':'cs','sleep':5,'key':[255, 255, 255, 255, 255, 255],'block':1,'keyboard_str':'%s{ENTER}'}
    serial = {'baudrate':115200,'port':'/dev/ttyS0'}
    lcd = {'welcome_m1':'Welcome','welcome_m2':'','ready_m1':'Ready','ready_m2':'','reading_m1':'Reading...','reading_m2':'','done_m1':'Done!','done_m2':'','error_m1':'Error','error_m2':'Check table','lcd_backlight':False}
    configuration = {'device':device,'serial':serial,'lcd':lcd}
    
    #*********************************
    #help function to read config file
    #*********************************
    def get_config_data(self,section,value):    
        try:
            if isinstance(self.configuration[section][value], bool):
                self.configuration[section][value] = self.config.getboolean(section, value)
            elif isinstance(self.configuration[section][value], int):
                self.configuration[section][value] = self.config.getint(section, value)
            elif isinstance(self.configuration[section][value], float):
                self.configuration[section][value] = self.config.getfloat(section, value)
            elif isinstance(self.configuration[section][value], list):
                self.configuration[section][value] = json.loads(self.config.get(section, value))
            else:
                self.configuration[section][value] = self.config.get(section, value)
                
        except ConfigParser.NoOptionError:
            self.config.set(section, value, self.configuration[section][value])


    #*******************
    #Loads configuration
    #*******************
    def load_config(self):
        self.config_file = self.main_dir + 'reader.conf'
        
        #get a dir path & create it if not exists
        dir = os.path.dirname(self.config_file)
        try:
            os.stat(dir)
        except:
            os.mkdir(dir)
            
        self.config = ConfigParser.RawConfigParser()
        
        #if config file exist,we can read it !
        if  os.path.isfile(self.config_file):
            self.config.read(self.config_file)
            try:
                
                for section in self.configuration:
                    if self.config.has_section(section):
                        for value in self.configuration[section]:
                            self.get_config_data(section,value)
                    else:
                        self.config.add_section(section)
                        for value in self.configuration[section]:
                            self.get_config_data(section,value)
                    
            except ConfigParser.Error:
                self.save_config()
                print 'Config file corupted, creating new'
        else:
            #writing config file & seting default values
            self.first_run = True
            self.save_config()
        
    #******
    #logger
    #******
    def logit(self, message = None, type='info'):
        if self.i18n:
            message = self.i18n.translate(message)
        file_log = False
        show = False
        message_time = time.strftime("%a, %d %b %Y %H:%M:%S ", time.localtime()) + ' ' + message
        if type == 'info':
            print message_time
        elif type == 'warning':
            show = gtk.MESSAGE_WARNING
            print message_time
        elif type == 'error':
            print message_time
            file_log = True
            show = gtk.MESSAGE_ERROR
            
        if file_log:
            error_file = open('error.log', 'a')
            error_file.write(message_time + "\n")
            error_file.close()
            
        if show:
            dialog = gtk.MessageDialog(
                parent         = None,
                flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
                type           = show,
                buttons        = gtk.BUTTONS_OK,
                message_format = message)
            dialog.set_title(message)
            dialog.connect('response', lambda dialog, response: dialog.destroy())
            dialog.show()

        
    
    
    #******************	
    #Save configuration
    #******************
    def save_config(self):
        for section in self.configuration:
            if self.config.has_section(section):
                for value in self.configuration[section]:
                    self.config.set(section, value, self.configuration[section][value])
        
        #self.config.set('device', 'key', json.dumps(self.key))
        self.logit('Saving configuration')
        
        # Writing our configuration file to config_file
        with open(self.config_file, 'wb') as configfile:
            self.config.write(configfile) 

    #*****************
    #Disconnect device  
    #*****************
    def disconnect(self, widget = None, button = None, data=None):
        if self.acr122l:
            self.clean()     
            self.acr122l.disconnect()
        self.menuItemBlight.set_sensitive(False)
        self.menuItemPolling.set_sensitive(False)
        self.menuItemConn.set_sensitive(True)
        self.menuItemDconn.set_sensitive(False)
        self.menuItemRead.set_sensitive(False)
        self.menuItemWrite.set_sensitive(False)
        self.menuItemCheck.set_sensitive(False)
        self.logit('Disconnected')

    #**************
    #Connect device
    #**************
    def connect(self, widget, button, data=None):

        try:
            self.acr122l = acr122l(self.configuration['serial']['port'], self.configuration['serial']['baudrate'])
        except Exception as exp:
            self.logit(str(exp),'error')
        if self.acr122l:
            if self.acr122l.is_connected():
                self.clean()
                self.menuItemBlight.set_sensitive(True)
                self.menuItemPolling.set_sensitive(True)
                self.menuItemDconn.set_sensitive(True)
                self.menuItemConn.set_sensitive(False)
                self.menuItemRead.set_sensitive(True)
                self.menuItemWrite.set_sensitive(True)
                self.menuItemCheck.set_sensitive(True)

                if self.configuration['lcd']['lcd_backlight']:
                    self.acr122l.LCD_back_light(True)
                self.lcd_states('welcome')
                self.logit('Connected')
            

    #********************
    #Controlong backlight
    #********************
    def back_light(self, widget, button, data=None):
        if widget.active:
            self.acr122l.LCD_back_light(True)
            self.configuration['lcd']['lcd_backlight'] = True
            self.logit('Backlight Enabled')
        else:
            self.acr122l.LCD_back_light(False)
            self.configuration['lcd']['lcd_backlight'] = False
            self.logit('Backlight Disabled')
        self.save_config()

    #**************************
    #Cleans device LCD and LEDs
    #**************************
    def clean(self):
        if self.acr122l.is_connected():
            self.acr122l.LCD_back_light(False)
            self.acr122l.LCD_Clear()
            self.acr122l.LED_control(False)
            self.logit('Cleaning device')

    #******************************
    #Shows configuration window
    #******************************
    def configure(self, widget=None, button=None, data=None):

        self.keyboard_string.set_text(self.configuration['device']['keyboard_str'])
        
        self.lcd_welcome_l1.set_text(self.configuration['lcd']['welcome_m1'])
        self.lcd_welcome_l2.set_text(self.configuration['lcd']['welcome_m2'])
        
        self.lcd_ready_l1.set_text(self.configuration['lcd']['ready_m1'])
        self.lcd_ready_l2.set_text(self.configuration['lcd']['ready_m2'])
        
        self.lcd_reading_l1.set_text(self.configuration['lcd']['reading_m1'])
        self.lcd_reading_l2.set_text(self.configuration['lcd']['reading_m2'])
        
        self.lcd_done_l1.set_text(self.configuration['lcd']['done_m1'])
        self.lcd_done_l2.set_text(self.configuration['lcd']['done_m2'])
        
        self.lcd_error_l1.set_text(self.configuration['lcd']['error_m1'])
        self.lcd_error_l2.set_text(self.configuration['lcd']['error_m2'])
        
        self.configure_win.queue_draw()
        self.configure_win.show_all()

    def lcd_states(self, state):
        self.acr122l.LCD_Clear()
        if self.configuration['lcd'][state + '_m1']:
            self.acr122l.LCD_Text(False,'A',0x00,self.configuration['lcd'][state + '_m1'])
        if self.configuration['lcd'][state + '_m2']:
            self.acr122l.LCD_Text(False,'A',0x40,self.configuration['lcd'][state + '_m2'])



    #*************************************
    #Sets config from configuration dialog
    #*************************************
    def set_config(self, widget, data=None): 
        if len(self.available_ports)>0:
            self.configuration['serial']['port'] = self.available_ports[self.cbox.get_active()]
            
        self.configuration['serial']['baudrate'] = int(self.available_baudrates[self.cbox_baudrate.get_active()])
        
        self.configuration['device']['keyboard_str'] = self.keyboard_string.get_text()
        if len(self.languages)>0:
            self.configuration['device']['language'] = self.languages[self.langbox.get_active()]
        
        self.configuration['lcd']['welcome_m1'] = self.lcd_welcome_l1.get_text()
        self.configuration['lcd']['welcome_m2'] = self.lcd_welcome_l2.get_text()
        
        self.configuration['lcd']['ready_m1'] = self.lcd_ready_l1.get_text()
        self.configuration['lcd']['ready_m2'] = self.lcd_ready_l2.get_text()
        
        self.configuration['lcd']['reading_m1'] = self.lcd_reading_l1.get_text()
        self.configuration['lcd']['reading_m2'] = self.lcd_reading_l2.get_text()
        
        self.configuration['lcd']['done_m1'] = self.lcd_done_l1.get_text()
        self.configuration['lcd']['done_m2'] = self.lcd_done_l2.get_text()
        
        self.configuration['lcd']['error_m1'] = self.lcd_error_l1.get_text()
        self.configuration['lcd']['error_m2'] = self.lcd_error_l2.get_text()
        
        self.hide_configure()
        self.save_config()

    #******************
    #Finds active ports
    #******************
    def find_ports(self):
        import serial
        for i in range(256):
            try:
                s = serial.Serial(i)
                self.available_ports.append(s.portstr)
                s.close() 
            except serial.SerialException:
                pass
                
        if os.name == 'posix':
            import glob
            linuxsers = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
            for s in linuxsers:
                if s not in self.available_ports:
                    self.available_ports.append(s)
        
    #******************
    #Opens pop up menu at systray icon
    #******************
    def popup_menu_cb(self, widget, button, time, data=None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)

    #**************************
    #hides configuration window
    #**************************
    def hide_configure(self, widget=None, button=None, data=None):
        self.configure_win.hide_all()
        return True

    #************
    #Destroys APP
    #************
    def destroy(self, widget, data=None):
        self.logit('Destroy signal occurred')
        self.poll_stop()
        self.disconnect()
        gtk.main_quit()
        
    def is_widget_int(self, widget=None, data=None):
        print ''
        
        
    #************************
    #Enables/Disables polling
    #************************	
    def polling(self, widget, button, data=None):
        if widget.active:
            self.poll()
            self.menuItemBlight.set_sensitive(False)
            self.menuItemRead.set_sensitive(False)
            self.menuItemDconn.set_sensitive(False)
            self.menuItemQit.set_sensitive(False)
            self.menuItemWrite.set_sensitive(False)
            self.menuItemCheck.set_sensitive(False)
        else:
            self.poll_stop()
            self.menuItemBlight.set_sensitive(True)
            self.menuItemRead.set_sensitive(True)
            self.menuItemDconn.set_sensitive(True)
            self.menuItemQit.set_sensitive(True)
            self.menuItemWrite.set_sensitive(True)
            self.menuItemCheck.set_sensitive(True)

    #**************
    #Starts polling
    #**************
    def poll(self, widget=None, data=None):
        self.acr122l.LED_control('1000')
        self.lcd_states('ready')
        self.polt = poolcard(self.acr122l, self)
        self.polt.start()

    #*************
    #Stops polling
    #*************
    def poll_stop(self, widget=None, data=None):
        if self.polt:
            self.polt.stop()

    #**********
    #Reads card
    #**********
    def read_card(self, widget=None, data=None,poll=None):
        if poll:
            self.poll_stop()
        if self.acr122l.TAG_Authenticate(0x00, self.configuration['device']['key']):
            self.logit('Starting read data')
            try:
                readed = self.acr122l.TAG_Read(self.configuration['device']['block'])
                if readed:
                    self.acr122l.LED_control('0010')
                    self.lcd_states('done')
                    to_keyboard = self.configuration['device']['keyboard_str'] % readed
                    self.virtkeys.press(to_keyboard)
                    self.acr122l.Buzzer_control(1,1,1)
                    time.sleep(self.configuration['device']['sleep'])
                else:
                    self.logit('Card is empty')
            except Exception as exp:
                    self.acr122l.LED_control('0001')
                    self.lcd_states('error')
                    self.logit('Error ocorupted while reading','error')
                    self.acr122l.Buzzer_control(10,10,1)
                
            if not poll:
                self.acr122l.LCD_back_light(self.configuration['lcd']['lcd_backlight'])
                self.acr122l.LED_control('1000')
                self.lcd_states('ready')
        else:
            self.logit('Authenticate failed','error')
        if poll:
            self.poll()
            
    #***********
    #Writes data
    #***********
    def write_card(self, data=None):
        if self.acr122l.TAG_Authenticate(0x00, self.configuration['device']['key']):
            self.logit('Starting write data')
            writed = self.acr122l.TAG_Update(self.configuration['device']['block'],data,'ASCII')
            if writed:
                self.acr122l.LED_control('0010')
                self.lcd_states('done')
                self.acr122l.Buzzer_control(1,1,1)
            else:
                self.acr122l.LED_control('0001')
                self.lcd_states('error')
                self.acr122l.Buzzer_control(10,10,1)
                
            time.sleep(self.configuration['device']['sleep'])
            self.acr122l.LCD_back_light(self.configuration['lcd']['lcd_backlight'])
            self.acr122l.LED_control('1000')
            self.lcd_states('ready')
        else:
            self.logit('Authenticate failed','error')

    
    def set_write(self, widget=None, data=None):
        text = self.write_data.get_text()
        if len(text)>16:
            self.logit('Data string is too long','error')
        else:
            self.write_card(text)
            self.hide_write()

    def write(self, widget=None, data=None):
        if self.acr122l.TAG_Authenticate(0x00, self.configuration['device']['key']):
            self.write_data.set_sensitive(True)
            readed = self.acr122l.TAG_Read(self.configuration['device']['block'])
            if readed:
                self.write_data.set_text(readed)
            else:
                self.write_data.set_text('')
        else:
            self.write_data.set_text(self.i18n.translate('No card detected'))
            self.write_data.set_sensitive(False)
        self.write_win.show_all()
        
        
    def hide_write(self, widget=None, data=None):
        self.write_win.hide()
        return True
        
    #*************
    #card Checking
    #*************
    def check_card(self, widget=None, data=None):
        if self.acr122l.TAG_Authenticate(0x00, self.configuration['device']['key']):

            kdata = self.acr122l.TAG_Read(self.configuration['device']['block'])
            ret = self.acr122l.TAG_Polling()
            uid = ''
            for r in ret['uid']:
                uid = uid + str(r) + ' '    
                     

            self.check_uid.set_text('UID: ' + uid)  
            if kdata:   
                self.check_data.set_text(self.i18n.translate('Data') + ': ' + kdata)
            else:
                self.check_data.set_text('')
            self.check_card_window.show_all()
        else:
            self.logit('No card detected','warning')
        
        
        
    def hide_check_card(self, widget=None, data=None):
        self.check_card_window.hide()
        return True

    def show_about(self, widget=None, data=None):
        self.about.show()


    def hide_about(self, widget=None, data=None):
        self.about.hide()

    #************************
    #Main init! and GUI build
    #************************
    def __init__(self):
            #run only once!
        try:
            SingleInstance()
        except IOError:
            print 'Another instance is already running'
        
        
        #************
        #About dialog
        #************
        self.about = gtk.AboutDialog()
        self.about.set_position(gtk.WIN_POS_CENTER)
        self.about.set_name("Reader")
        self.about.set_program_name("Reader")
        self.about.set_version(self.version)
        self.about.set_comments('Reader is appliacion for reading/writing NFC cards using acr122L NFC reader')
        self.about.set_license('Proprietary right now')
        self.about.set_website('http://sg1-game.net/')
        author = ['Adam Schubert']
        self.about.set_authors(author)
        self.about.connect("response",  self.hide_about)

        #loads configuration
        self.load_config()
        
        #we have icon ?
        if os.path.isfile(self.icon)!=True:
            self.icon = 'reader/'+ self.icon
            print 'Icon not found'
        elif os.path.isfile(self.icon)!=True:
            self.icon = False
   
        
        self.i18n = i18n(self.configuration['device']['language'])
        self.languages = self.i18n.languages()
        #inicialize virtual keyboard
        self.virtkeys = virtkeys()
        
        #*************
        #Config window
        #*************
        #find serial ports
        self.find_ports()

       
        # create a new configure window
        self.configure_win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.configure_win.set_position(gtk.WIN_POS_CENTER)
        if self.icon:
            self.configure_win.set_icon_from_file(self.icon)
        self.configure_win.set_title(self.i18n.translate('Configuration'))
        self.configure_win.connect("delete_event", self.hide_configure)

        # Sets the border width of the window.
        self.configure_win.set_border_width(10)


        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)

        #conn config
        tabname = self.i18n.translate('Connecion')

        frame = gtk.Frame(tabname)
        frame.set_border_width(10)
        frame.set_size_request(100, 75)
        

        fixed_connecion = gtk.Fixed()

        #Serial box selecion
        self.cbox = gtk.combo_box_new_text()
        cnt = 0
        if self.available_ports:
            for p in self.available_ports:
                self.cbox.append_text(p)
                if p == self.configuration['serial']['port']:
                    self.cbox.set_active(cnt)
                cnt = cnt + 1
        else:
            self.cbox.append_text(self.i18n.translate('No ports found'))
            self.cbox.set_active(0)
            self.cbox.set_sensitive(False)
        
        vbox_serial_conf = gtk.HBox()
        vbox_serial_conf.pack_start(gtk.Label(self.i18n.translate('Port') + ':'))
        vbox_serial_conf.pack_start(self.cbox)
        
        self.cbox_baudrate = gtk.combo_box_new_text()
        cnt = 0
        for p in self.available_baudrates:
                self.cbox_baudrate.append_text(str(p))
                if p == self.configuration['serial']['baudrate']:
                    self.cbox_baudrate.set_active(cnt)
                cnt = cnt + 1
                
        vbox_baudrate_conf = gtk.HBox()
        vbox_baudrate_conf.pack_start(gtk.Label(self.i18n.translate('Baudrate') + ':'))
        vbox_baudrate_conf.pack_start(self.cbox_baudrate)
                
        #FIXME ZAKOMENTOVANA VOLBA RYCHLOSTI
        #vbox.pack_start(vbox_baudrate_conf)
        vbox_serial_conf.set_size_request(350, -1)
        fixed_connecion.put(vbox_serial_conf, 0, 0)
        frame.add(fixed_connecion)

        label = gtk.Label(tabname)
        notebook.append_page(frame, label)
        
        #LCD Config
        tabname = self.i18n.translate('Display')

        frame = gtk.Frame(tabname)
        frame.set_border_width(10)
        frame.set_size_request(100, 75)

        vbox_lcd = gtk.VBox()
        
        #---Welcome------------------
        self.lcd_welcome_l1 = gtk.Entry(self.lcd_size)
        self.lcd_welcome_l2 = gtk.Entry(self.lcd_size)

        welcome_frame = gtk.Frame(self.i18n.translate('Welcome message'))
        
        vbox_welcome = gtk.VBox()
        vbox_welcome.pack_start(self.lcd_welcome_l1)
        vbox_welcome.pack_start(self.lcd_welcome_l2)
        
        welcome_frame.add(vbox_welcome)
        vbox_lcd.pack_start(welcome_frame)
        

        
        
        #---Ready------------------
        self.lcd_ready_l1 = gtk.Entry(self.lcd_size)
        self.lcd_ready_l2 = gtk.Entry(self.lcd_size)

        ready_frame = gtk.Frame(self.i18n.translate('Ready message'))
        
        vbox_ready = gtk.VBox()
        vbox_ready.pack_start(self.lcd_ready_l1)
        vbox_ready.pack_start(self.lcd_ready_l2)
        
        ready_frame.add(vbox_ready)
        vbox_lcd.pack_start(ready_frame)
        
        
        
        #---Reading------------------     
        self.lcd_reading_l1 = gtk.Entry(self.lcd_size)
        self.lcd_reading_l2 = gtk.Entry(self.lcd_size)

        reading_frame = gtk.Frame(self.i18n.translate('Reading message'))
        
        vbox_reading = gtk.VBox()
        vbox_reading.pack_start(self.lcd_reading_l1)
        vbox_reading.pack_start(self.lcd_reading_l2)
        
        reading_frame.add(vbox_reading)
        vbox_lcd.pack_start(reading_frame)
        
        
        

        #---Done------------------      
        self.lcd_done_l1 = gtk.Entry(self.lcd_size)
        self.lcd_done_l2 = gtk.Entry(self.lcd_size)

        done_frame = gtk.Frame(self.i18n.translate('Done message'))
        
        vbox_done = gtk.VBox()
        vbox_done.pack_start(self.lcd_done_l1)
        vbox_done.pack_start(self.lcd_done_l2)
        
        done_frame.add(vbox_done)
        vbox_lcd.pack_start(done_frame)
        
        
        
        #---Error------------------
        self.lcd_error_l1 = gtk.Entry(self.lcd_size)
        self.lcd_error_l2 = gtk.Entry(self.lcd_size)

        error_frame = gtk.Frame(self.i18n.translate('Error message'))
        
        vbox_error = gtk.VBox()
        vbox_error.pack_start(self.lcd_error_l1)
        vbox_error.pack_start(self.lcd_error_l2)
        
        error_frame.add(vbox_error)
        vbox_lcd.pack_start(error_frame)
        
        
        frame.add(vbox_lcd)

        label = gtk.Label(tabname)
        notebook.append_page(frame, label)
        
        #Output
        tabname = self.i18n.translate('Output')

        frame = gtk.Frame(tabname)
        frame.set_border_width(10)
        frame.set_size_request(100, 75)

        fixed_output = gtk.Fixed()

        #Keyboard send string
        self.keyboard_string = gtk.Entry(0)
        hbox_keyboard = gtk.HBox()
        hbox_keyboard.pack_start(gtk.Label(self.i18n.translate('Keyboard output string')))
        hbox_keyboard.pack_start(self.keyboard_string)
        hbox_keyboard.set_size_request(350, -1)
        fixed_output.put(hbox_keyboard, 0, 0)
        
        #language 
        self.langbox = gtk.combo_box_new_text()
        cnt = 0
        if self.languages:
            for l in self.languages:
                self.langbox.append_text(l)
                if l == self.configuration['device']['language']:
                    self.langbox.set_active(cnt)
                cnt = cnt + 1
        else:
            self.langbox.append_text(self.i18n.translate('No laguage files found'))
            self.langbox.set_active(0)
            self.langbox.set_sensitive(False)
        
        
        hbox_lang = gtk.HBox()
        hbox_lang.pack_start(gtk.Label(self.i18n.translate('Language')))
        hbox_lang.pack_start(self.langbox)
        hbox_lang.set_size_request(350, -1)
        fixed_output.put(hbox_lang, 0, 50)
        
        
        
        frame.add(fixed_output)

        label = gtk.Label(tabname)
        notebook.append_page(frame, label)
        
        
        #Card
        #tabname = 'Card'

        #frame = gtk.Frame(tabname)
        #frame.set_border_width(10)
        #frame.set_size_request(100, 75)
        #self.block = gtk.Entry(3)

        #vbox_card = gtk.VBox()
        #block_label= gtk.Label('Block')
        #block_box = gtk.HBox()
        #block_box.pack_start(block_label)
        #block_box.pack_start(self.block)

        #key_box = gtk.HBox()
        #key_label= gtk.Label('Key')
        #key_box.pack_start(key_label)
        #for i in range(1,6):
        #    self.key = gtk.Entry(3)
        #    self.key.set_width_chars(3)
        #    key_box.pack_start(self.key)
        #vbox_card.pack_start(block_box)
        #vbox_card.pack_start(key_box)
        #frame.add(vbox_card)

        #label = gtk.Label(tabname)
        #notebook.append_page(frame, label)
        
        
        
        #table.attach(notebook, 0,6,0,1)
        
        fixed = gtk.Fixed()
        notebook.set_size_request(500,500)
        fixed.put(notebook, 0, 0)
        

        #Configure OK button
        button_ok_config = gtk.Button(stock=gtk.STOCK_OK)
        button_ok_config.connect("clicked", self.set_config, None)
        fixed.put(button_ok_config, 350, 513)
        
        button_storno_config = gtk.Button(stock=gtk.STOCK_CANCEL)
        button_storno_config.connect("clicked", self.hide_configure, None)
        fixed.put(button_storno_config, 155, 513)
        

        self.configure_win.set_resizable(False)
        self.configure_win.add(fixed)

        #************
        #Write window
        #************
        # create a new write window
        self.write_win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.write_win.set_position(gtk.WIN_POS_CENTER)
        self.write_win.set_title(self.i18n.translate('Write data'))
        self.write_win.connect("delete_event", self.hide_write)
        # Sets the border width of the window.
        self.write_win.set_border_width(10)

        self.button = gtk.Button(stock=gtk.STOCK_OK)
        self.button.connect("clicked", self.set_write, None)

        self.write_data = gtk.Entry(16)
        self.write_data.connect("activate", self.set_write, None)

        vbox = gtk.VBox()
        vbox.pack_start(self.write_data)
        vbox.pack_start(self.button)

        self.write_win.add(vbox)
        
        
        #*****************
        #Check card window
        #*****************
        # create a new check window
        self.check_card_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.check_card_window.set_position(gtk.WIN_POS_CENTER)
        self.check_card_window.set_title(self.i18n.translate('Check card'))
        self.check_card_window.connect("delete_event", self.hide_check_card)
        # Sets the border width of the window.
        self.check_card_window.set_border_width(10)

        self.button = gtk.Button(stock=gtk.STOCK_OK)
        self.button.connect("clicked", self.hide_check_card, None)

        vbox = gtk.VBox()
        self.check_uid = gtk.Label()
        self.check_data = gtk.Label()
        vbox.pack_start(self.check_uid)
        vbox.pack_start(self.check_data)
        vbox.pack_start(self.button)

        self.check_card_window.add(vbox)
        

        #************
        #Systray ICON
        #************

        self.statusicon = gtk.StatusIcon()
        if self.icon:
            self.statusicon.set_from_file(self.icon)
        #self.statusicon.connect("activate",self.configure)

        #************
        #systray MENU 
        #************
        menu = gtk.Menu()

        #connect
        self.menuItemConn = gtk.ImageMenuItem(gtk.STOCK_CONNECT)
        self.menuItemConn.connect('activate', self.connect, self.statusicon)
        menu.append(self.menuItemConn)

        #disconnect
        self.menuItemDconn = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
        self.menuItemDconn.connect('activate', self.disconnect, self.statusicon)
        self.menuItemDconn.set_sensitive(False)
        menu.append(self.menuItemDconn)

        #read
        self.menuItemRead = gtk.ImageMenuItem(self.i18n.translate('Read'))
        self.menuItemRead.connect('activate', self.read_card, self.statusicon)
        self.menuItemRead.set_sensitive(False)
        menu.append(self.menuItemRead)
        
        #write
        self.menuItemWrite = gtk.ImageMenuItem(self.i18n.translate('Write'))
        self.menuItemWrite.connect('activate', self.write, self.statusicon)
        self.menuItemWrite.set_sensitive(False)
        menu.append(self.menuItemWrite)

        #Check card
        self.menuItemCheck = gtk.ImageMenuItem(self.i18n.translate('Check card'))
        self.menuItemCheck.connect('activate', self.check_card, self.statusicon)
        self.menuItemCheck.set_sensitive(False)
        menu.append(self.menuItemCheck)	

        #configure
        self.menuItemConf = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        self.menuItemConf.connect('activate', self.configure, self.statusicon)
        menu.append(self.menuItemConf)		

        #Polling
        self.menuItemPolling = gtk.CheckMenuItem(self.i18n.translate('Enable Polling'))
        self.menuItemPolling.set_sensitive(False)

        self.menuItemPolling.connect('activate', self.polling, self.statusicon)
        menu.append(self.menuItemPolling)


        #backlight
        self.menuItemBlight = gtk.CheckMenuItem(self.i18n.translate('Enable Backlight'))
        self.menuItemBlight.set_sensitive(False)
        if self.configuration['lcd']['lcd_backlight']:
            self.menuItemBlight.set_active(True)

        self.menuItemBlight.connect('activate', self.back_light, self.statusicon)
        menu.append(self.menuItemBlight)

        #About
        self.menuItemQit = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        self.menuItemQit.connect('activate', self.show_about, self.statusicon)
        menu.append(self.menuItemQit)

        #quit button
        self.menuItemQit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItemQit.connect('activate', self.destroy, self.statusicon)
        menu.append(self.menuItemQit)

        self.statusicon.connect("popup-menu",self.popup_menu_cb, menu)

        if self.first_run:
            self.configure()

    #*************
    #Main function
    #*************
    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()


# If the program is run directly or passed as an argument to the python
# interpreter then create a reader instance and show it
if __name__ == "__main__":
    reader = reader()
    reader.main()
