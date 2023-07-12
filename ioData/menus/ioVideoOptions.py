from pycel import *
import cPickle
import urllib2
import socket

import Menu
import ioScroller
import ioDataBin

#A widget inside the options screen
class ioVideoOptions:
    api_version = 2
    
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.x = 82500
        self.y = 62500
        self.menu = Menu.ioMenu(self.entity)
        
        volabel = celCreateBillboard(pl, self.entity)
        volabel.text_font_size = self.fconst * 1.25
        volabel.text_font ='/outlaws/fonts/lcd2.ttf'
        volabel.text = 'Video Output (Applied on Restart)'
        volabel.text_fg_color = self.fcolor
        volabel.x = self.x
        volabel.y = self.y
        
        res = celCreateBillboard(pl, self.entity)
        res.x = self.x
        res.y = self.y + 10000
        res.text_font_size = self.fconst
        res.text_fg_color = self.fcolor
        res.text_font = '/outlaws/fonts/lcd2.ttf'
        res.text = 'Resolution:'
        
        self.resscroller = ioScroller.ioScroller(self.entity, [self.x + 40000, self.y + 10000], [70000, 50000], '_resscroller')
        reslist = ['320x240',
                   '640x480',
                   '800x600',
                   '1024x768',
                   '1280x1024',
                   '1600x1200',
                   '1920x1200',
                   '1280x800',
			 '1680x1050',
                   '1600x1024']
        for res in reslist:
            self.resscroller.additem(res, 'resscroller_select')
        
        fslabel = celCreateBillboard(pl, self.entity)
        fslabel.text_font_size = self.fconst
        fslabel.text_font ='/outlaws/fonts/lcd2.ttf'
        fslabel.text = 'Fullscreen:'
        fslabel.text_fg_color = self.fcolor
        fslabel.x = self.x
        fslabel.y = self.y + 60000
        
        fsbpos = [self.x + 40000, self.y + 60000]
        fsbsize = [15000, 10000]
        self.fsbutton = self.menu.addElement('FS', 'fsbutton_clicked', fsbpos, fsbsize, self.fconst, 'button-bg')
        
        fxlabel = celCreateBillboard(pl, self.entity)
        fxlabel.text_font_size = self.fconst * 1.25
        fxlabel.text_font ='/outlaws/fonts/lcd2.ttf'
        fxlabel.text = 'Effects'
        fxlabel.text_fg_color = self.fcolor
        fxlabel.x = self.x
        fxlabel.y = self.y + 90000
        
        dustlabel = celCreateBillboard(pl, self.entity)
        dustlabel.text_font_size = self.fconst
        dustlabel.text_font ='/outlaws/fonts/lcd2.ttf'
        dustlabel.text = 'Dust trails:'
        dustlabel.text_fg_color = self.fcolor
        dustlabel.x = self.x
        dustlabel.y = self.y + 100000
        
        dustbpos = [self.x + 40000, self.y + 100000]
        dustbsize = [15000, 10000]
        self.dtbutton = self.menu.addElement('dust', 'dtbutton_clicked', dustbpos, dustbsize, self.fconst, 'button-bg')
  
        foliage = celCreateBillboard(pl, self.entity)
        foliage.x = self.x
        foliage.y = self.y + 120000
        foliage.text_font_size = self.fconst
        foliage.text_fg_color = self.fcolor
        foliage.text_font = '/outlaws/fonts/lcd2.ttf'
        foliage.text = 'Foliage:'
        
        self.foliagescroller = ioScroller.ioScroller(self.entity, [self.x + 40000, self.y + 120000], [70000, 40000], '_foliagescroller')
        self.foliagescroller.menu.clear()
        for level in ['High', 'Low', 'Off']:
            self.foliagescroller.additem(level, 'foliagescroller_select')
  
        self.loadconfig()
        
    #Load from the cs config system and set the widgets to reflect these settings
    def loadconfig(self):
        x = str(Config.GetInt('Video.ScreenWidth', 800))
        y = str(Config.GetInt('Video.ScreenHeight', 600))
        self.resscroller.selectname(x + 'x' + y)
        
        fs = Config.GetBool('Video.FullScreen', True)
        fsbb = celBillboard(self.fsbutton)
        if fs:
            fsbb.text = 'Yes'
        else:
            fsbb.text = 'No'
            
        dt = Config.GetBool('Outlaws.Settings.Video.DustTrails', True)
        dtbb = celBillboard(self.dtbutton)
        if dt:
            dtbb.text = 'Yes'
        else:
            dtbb.text = 'No'
            
        foliage = Config.GetStr('Outlaws.Settings.Video.Foliage', 'High')
        self.foliagescroller.selectname(foliage)
        
    def scroller_down_resscroller(self, pc, args):
        self.resscroller.scrolldown()
        
    def scroller_up_resscroller(self, pc, args):
        self.resscroller.scrollup()
        
    def resscroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.resscroller.selectname(name)
        
    def foliagescroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.foliagescroller.selectname(name)
        
    #Toggle fullscreen on/off
    def fsbutton_clicked(self, pc, args):
        fsbb = celBillboard(self.fsbutton)
        if fsbb.text == 'No':
            fsbb.text = 'Yes'
        elif fsbb.text == 'Yes':
            fsbb.text = 'No'
           
    #Toggle dust trails on/off
    def dtbutton_clicked(self, pc, args):
        dtbb = celBillboard(self.dtbutton)
        if dtbb.text == 'No':
            dtbb.text = 'Yes'
        elif dtbb.text == 'Yes':
            dtbb.text = 'No'
        
    #Write back to cs config system
    def save(self, pc, args):
        bmap = {'No' : False, 'Yes' : True}
        
        resx, resy = self.resscroller.selectedname.split('x')
        Config.SetInt('Video.ScreenWidth', int(resx))
        Config.SetInt('Video.ScreenHeight', int(resy))
        
        fs = celBillboard(self.fsbutton).text
        Config.SetBool('Video.FullScreen', bmap[fs])
        
        dt = celBillboard(self.dtbutton).text
        Config.SetBool('Outlaws.Settings.Video.DustTrails', bmap[dt])
        
        flevel = self.foliagescroller.selectedname
        Config.SetStr('Outlaws.Settings.Video.Foliage', flevel)
        
        Config.Save()
        
    def destruct(self, pc, args):
        self.menu.clear()
        self.resscroller.destruct()
        self.foliagescroller.destruct()
        self.entity.PropertyClassList.RemoveAll()