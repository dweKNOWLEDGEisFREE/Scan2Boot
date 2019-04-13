#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Scan2Boot - Boot and information screen.

    This program is part of the Scan2 Suite.
    https://github.com/dweKNOWLEDGEisFREE

    This program is licensed under the GNU General Public License v3.0

    Copyright 2019 by David Weyand, Ernst Schmid


apt-get install sudo

Tools: pip install urwid
       pip install urwid_utils
       pip install additional-urwid-widgets
       pip install pudb
       pip install asyncio
       pip install twisted
       pip install netifaces
       
Debugging: python3 -m pudb.run scan2Boot.py

Usefull programs: lynx, mc, aptitude, sysv-rc-conf.
                  ip address, crontab -e, top, bpython
                  chmod 777 *.py, mysql

Installing the script:

Create user.: adduser scan2
Change shell: chsh scan2
            | /home/scan2/scan2Boot.py
Change sudo.: Add line ... to /etc/sudoers
            | scan2 ALL=NOPASSWD:ALL
Mod systemd : modify file /lib/systemd/system/getty@service
            | ...
            | [Service]
            | # the VT is cleared by TTYVTDisallocate
            | #ExecStart=-/sbin/agetty --noclear %I $TERM
            | ExecStart=-/sbin/agetty --noclear --autologin scan2 %I $TERM
            | ...

'''

import os, sys
import urwid.curses_display
import netifaces
from additional_urwid_widgets.widgets.message_dialog import MessageDialog

def_scr = urwid.curses_display.Screen()

def_pal = [('logo',  'white,bold',     'black'     ),
           ('error', 'dark red,bold',  'black'     ),
           ('info',  'dark green,bold','black'     ),
           ('popbg', 'white',          'dark blue' ),
           ('btnOK', 'white,bold',     'dark red'  ),
           ('btnGO', 'white,bold',     'dark green'),
           ('btnXX', 'white,bold',     'light gray'),]

def_txt = (u"S u i t e   Version 0.10\n\n"+
           u"Data Acquisition Services\nfor iTop with TeemIP.\n"+
           u"Modules: Scan2IP Scan2VMware Scan2Agent")

def_url = (u"Updates, documentation and FAQ are available at:\n\n"+
           u"https://github.com/dweKNOWLEDGEisFREE\n\n\n"+
           u"Please visit the following URLs to configure each service.\n")



class SwitchingPadding(urwid.Padding):
    def padding_values(self, size, focus):
        maxcol = size[0]
        width, ignore = self.original_widget.pack(size, focus=focus)
        if maxcol > width:
            self.align = "left"
        else:
            self.align = "right"
        return urwid.Padding.padding_values(self, size, focus)

''' Main window with all informations about the software.
'''
def MainWin():
    def ip_access():
        # LIST ALL INTERFACES
        txt = []
        for i in netifaces.interfaces():
            # NO LOOPBACK
            if i=="lo":
                continue
            # EXTRACT IPv4
            try:
                ipStr=netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']
            except:
                continue
            # GENERATE INFO TEXT
            txt.append(u"\n")
            txt.append(u"scan2IP....: ")
            txt.append(('logo', u"http://"+ipStr+":5000\n"))
            txt.append(u"scan2Agent.: ")
            txt.append(('logo', u"http://"+ipStr+":5001\n"))
            txt.append(u"scan2VMware: ")
            txt.append(('logo', u"http://"+ipStr+":5002\n"))
        # CHECK RESULTS
        if len(txt)==0:
            return [('error', u"\nERROR: "),
                    u"IP ADDRESS FOR WEB ACCESS NOT AVAILABLE"]                
        else:
            return [def_url]+txt

    # HEADER
    # BigText -> AddrWrap -> Filler -> BoxAdapter
    bt = urwid.BigText("Scan2", None)
    bt.set_font(urwid.Thin6x6Font())
    bt = SwitchingPadding(bt, 'left', None)
    bt = urwid.AttrWrap(bt, 'bigtext')
    bt = urwid.Filler(bt, 'bottom', None, 5)
    bt = urwid.BoxAdapter(bt, 5)
    # Columns (LOGO, TEXT)
    hd = urwid.AttrMap(urwid.Text(def_txt), 'logo')
    hd = urwid.Columns([(32,bt),hd,])
    # BODY
    ci = ip_access()
    ci = urwid.Filler(urwid.Text(ci), valign='top', top=2, bottom=1)
    # MENU
    mn = urwid.Text([('logo', u"<F2>"), u" Customize System   ",
                     ('logo', u"<F3>"), u" Shell   ",
                     ('logo', u"<F4>"), u" Restart   ",
                     ('logo', u"<F5>"), u" Shut Down", ])
    # SCREEN
    sc = urwid.Frame(header=hd, body=ci, footer=mn)
    sc = urwid.Padding(sc, left=1, right=1)
    sc = urwid.LineBox(sc)
    return sc

        
if __name__ == '__main__':
    def handle_key(key):
        if loop.widget != mw:
            return
    #   if key in ('q', 'Q'):
    #       quitPrg()
        if key in ('f2', 'F2'):
            dlgConfig()
        if key in ('f3', 'F3'):
            dlgShell()
        if key in ('f4', 'F4'):
            dlgReboot()
        if key in ('f5', 'F5'):
            dlgShutdown()

    def quitPrg(*args, **kwargs):
        raise urwid.ExitMainLoop()

    # Back to original view
    def show_main(key):
        loop.widget = mw

    # Network Configuration
    def dlgConfig():
        """ part of network manager """
        loop.screen.stop()
    #   cmd=('nmtui-edit')
        cmd=('sudo ./edit.py /etc/network/interfaces')
        os.system(cmd)
        loop.screen.start()

    # System Shell        
    def cmd_shell(key):
        loop.screen.stop()
        print("\n\nExit the system shell by entering: exit\n")
        sys.stdout.flush()
        sys.stderr.flush()
    #   cmd=('sh')
        cmd=('sudo bash')
        os.system(cmd)
        loop.screen.start()
        show_main(key)

    # Rebooting        
    def cmd_reboot(key):
        loop.screen.stop()
        cmd=('sudo reboot')
        os.system(cmd)
        loop.screen.start()
        show_main(key)

    # Shutting Down        
    def cmd_shutdown(key):
        loop.screen.stop()
    #   cmd=('sudo halt')
        cmd=('sudo poweroff')
        os.system(cmd)
        loop.screen.start()
        show_main(key)

    # Dialog Shell
    def dlgShell():
        contents = [('info', u"\nStarting system shell."),]
        btnXX = urwid.AttrMap(urwid.Button("Cancel", show_main), "", "btnXX") 
        btnOk = urwid.AttrMap(urwid.Button("SHELL", cmd_shell), "", "btnGO")
        btns = [btnXX, btnOk]
        loop.widget = MessageDialog(contents, btns, (30, 7),
                                    contents_align= "center",
                                    title=" I N F O ", background=mw)

    # Dialog Shut Down
    def dlgReboot():
        contents = [('error', u"\nRebooting the system?"),]
        btnXX = urwid.AttrMap(urwid.Button("Cancel", show_main), "", "btnXX") 
        btnOk = urwid.AttrMap(urwid.Button("REBOOT", cmd_reboot), "", "btnOK")
        btns = [btnXX, btnOk]
        loop.widget = MessageDialog(contents, btns, (30, 7),
                                    contents_align= "center",
                                    title=" W A R N I N G ", background=mw)

    # Dialog Shut Down
    def dlgShutdown():
        contents = [('error', u"\nShutting down system?"),]
        btnXX = urwid.AttrMap(urwid.Button("Cancel", show_main), "", "btnXX") 
        btnOk = urwid.AttrMap(urwid.Button("SHUT DOWN", cmd_shutdown), "", "btnOK")
        btns = [btnXX, btnOk]
        loop.widget = MessageDialog(contents, btns, (30, 7),
                                    contents_align= "center",
                                    title=" W A R N I N G ", background=mw)

    # SHOW PARAMETERS
    print('scan2Boot: #['+str(len(sys.argv))+'] ['+str(sys.argv)+']')
    # SHOW PATH
    print('scan2Boot: Path - ',sys.argv[0])
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    print ("scan2Boot: running from - ", dirname)
    os.chdir(dirname)
    # SHOW USER ID
    print('scan2Boot: Real UserID - %d' % os.getuid())
    print('scan2Boot: Effective UserID - %d' % os.geteuid())
    # Flushing buffers ...
    sys.stdout.flush()
    sys.stderr.flush()

    # MAGIC ...
    mw=MainWin()
    loop = urwid.MainLoop(mw, screen=def_scr, palette=def_pal,
                          handle_mouse=False, unhandled_input=handle_key)
    loop.run()

