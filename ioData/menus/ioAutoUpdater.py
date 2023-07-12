from pycel import *
import os
import subprocess
import sys

import ioInit
import ioDataBin
import ioLoader
import ioBaseInit
import Menu
import ioScroller
import ioDownloader
#Checks to see if there is a new version available
        
class ioAutoUpdater:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        
        bg = celAddBillboard(self.entity)
        bg.materialnamefast = 'blackbg'
        bg.width = 307200
        bg.height = 307200
        bg.x = 0
        bg.y = 0
        
        #Splash screen
        splashscreen = celAddBillboard(self.entity)
        splashscreen.materialnamefast = 'titleback'
        splashscreen.width = 307200
        splashscreen.height = 207200
        splashscreen.x = 0
        splashscreen.y = 30000
        
        self.fconst = Menu.GetFontConstant()
        
        #Our descriptive label
        self.label = celAddBillboard(self.entity)
        self.label.x = 20000
        self.label.y = 225000
        self.label.text_font_size = self.fconst
        self.label.text_font = '/outlaws/fonts/lcd2.ttf'
        self.label.text = 'Checking for updates...'
        
        self.barbg = celAddBillboard(self.entity)
        self.barbg.x = 20000
        self.barbg.y = 235000
        self.barbg.width = 50000
        self.barbg.height = 10000
        self.barbg.materialnamefast = 'button-bg'
        
        self.pbar = celAddBillboard(self.entity)
        self.pbar.x = 20000
        self.pbar.y = 235000
        self.pbar.width = 0
        self.pbar.height = 10000
        self.pbar.materialnamefast = 'button-bg'
        
        self.menu = Menu.ioMenu(self.entity)
        self.menu.addElement('Abort', 'Abort_clicked', (25000, 255000), (18000, 9000), self.fconst, 'button-bg')

        #Filename and address of the patch we are downloading
        self.patchaddr = ''
        self.patchfilename = ''
        
        self.version = Config.GetStr('Outlaws.Version.Name')
        self.state = 'gettingversions'
        self.mirror = Config.GetStr('Outlaws.Updates.Address', '')
        self.dl = ioDownloader.ioDownloader(self.mirror + '/versions.txt')
        self.dl.start()
        
        timer = celTimer(self.entity)
        timer.WakeUpFrame(0)
        
        #A scroller is popped up if an update is available
        self.desc = None
        self.descbg = None
        
        self.updateskipped = False
    
    #Empty out the the downloader's event que
    def pctimer_wakeupframe(self, pc, args):
        ioDownloader.dispatch(self, self.dl)
            
    def downloader_read(self, pars):
        pc = float(self.dl.read) / float(self.dl.size)
        #Yay! We're done
        if pc >= 1.0:
            pc = 1.0
            
        #Set the progress bar
        self.pbar.width = int(pc * self.barbg.width)
        
    def downloader_error(self, pars):
        error = pars[0] 
        self.completeupdate('Error getting %s, %s' % (self.dl.url, error), 4000)
            
    def downloader_complete(self, pars):
        if self.state == 'gettingversions':
            self.handleversions()
        elif self.state == 'gettingpatches':
            self.handlepatches()
            
    #Work out what to do with the versions file
    def handleversions(self):
        self.state = 'waiting'
        info = ioLoader.parsefile(self.dl.data)
        self.patchlist = info['Patchlist']
        self.label.text = 'Finished checking'
        latest = info['Latest Version'][0]
        #There is a new version
        if latest > Config.GetStr('Outlaws.Version.Name'):
            self.makedescwindow()
            self.desc.additem('New version available - %s' % latest, '')
            self.desc.additem('', '')
            for line in info['Description']:
                self.desc.additem(line, '')
            #Now give the buttons
            self.menu.clear()
            self.menu.addElement('Skip', 'Abort_clicked', (115000, 235000), (18000, 9000), self.fconst, 'button-bg')
            self.menu.addElement('Update', 'Update_clicked', (155000, 235000), (18000, 9000), self.fconst, 'button-bg')
        else:
            self.completeupdate('No updates available', 2000)
    
    #Show the popup window thingy with info
    def makedescwindow(self):
        sw = 130000
        sh = 160000
        sx = 88600
        sy = 60000
        #makes it appear nicer
        self.descbg = celAddBillboard(self.entity)
        self.descbg.x = sx
        self.descbg.y = sy
        self.descbg.width = sw
        self.descbg.height = sh
        self.descbg.materialnamefast = 'darkblack'
        self.desc = ioScroller.ioScroller(self.entity, [sx, sy], [sw, sh])
        self.desc.allowdoubles = True
        self.desc.spacing = 7000
        
    def killdescwindow(self):
        if self.desc:
            self.desc.destruct()
            self.desc = None
        if self.descbg:
            self.entity.PropertyClassList.Remove(self.descbg)
            self.descbg = None
        
    def Abort_clicked(self, pc, args):
        self.updateskipped = True
        self.completeupdate('Update aborted', 1000)
        
    #Time to start the update process
    def Update_clicked(self, pc, args):
        self.killdescwindow()
        self.menu.clear()
        self.menu.addElement('Cancel', 'Abort_clicked', (25000, 255000), (18000, 9000), self.fconst, 'button-bg')
        self.clearpatchdir()
        self.createpatchlist()
        #Time to start downloading the patches
        self.handlepatches()

    #Clear out the patches directory
    def clearpatchdir(self):
        #Empty out the folder bottom up
        for subroot, subfolders, subfiles in os.walk('patches', topdown = False):
            for subfile in subfiles:
                try:
                    os.remove('%s/%s' % (subroot, subfile))
                except:
                    print 'couldnt empty folder', subroot
                    break
                try:
                    os.rmdir(subroot)
                except:
                    print 'couldnt remove folder', subroot
        try:
            os.mkdir('patches')
        except OSError:
            pass
            
    #Work out which patches we actually need to download
    def createpatchlist(self):
        #Reformat the patchlist using tuples at the ':' split
        patches = []
        for entry in self.patchlist:
            pair = entry.split(':')
            name = pair[0].strip()
            file = pair[1].strip()
            patches.append((name, file))
        #Now filter out the versions below us
        self.patchlist = [(n, f) for (n, f) in patches if n > self.version]
        #Write out the patchlist
        patchfile = open('patches/patches.txt', 'w')
        map(lambda f: patchfile.write(f[1] + '\n'), self.patchlist)
        patchfile.close()
        
    #Download the next patch we need
    def handlepatches(self):
        self.state = 'gettingpatches'
        #Write out the patch we just finished
        if self.patchaddr == self.dl.url:
            f = open('patches/%s' % self.patchfilename, 'wb')
            f.write(self.dl.data)
            f.close()
        #Download the next patch
        if len(self.patchlist) > 0:
            self.patchfilename = self.patchlist.pop(0)[1]
            self.patchaddr = self.mirror + '/' + self.patchfilename
            self.label.text = 'Fetching %s' % self.patchaddr
            self.dl = ioDownloader.ioDownloader(self.patchaddr)
            self.dl.start()
        #All downloads have finished, drop out of hte game and run the updater script
        else:
            self.label.text = 'Finished downloading patches'
            self.makedescwindow()
            self.desc.additem('All the updated have finished downloading.', '')
            self.desc.additem('Press Continue to drop out of the game and', '')
            self.desc.additem('apply the updates. Once the updates are', '')
            self.desc.additem('installed, the game will restart.', '')
            self.menu.clear()
            self.menu.addElement('Continue', 'Continue_clicked', (155000, 235000), (22000, 9000), self.fconst, 'button-bg')
            
    #Run the updater script and quit the game
    def Continue_clicked(self, pc, args):
        ioInit.exitgame()
        if os.name == 'posix':
            subprocess.Popen(['python', 'ioData/scripts/update.py'], shell = False)
        else:
            subprocess.Popen(['ioData\scripts\update.bat'], shell = False)
        
    #Finish up, but show a message for a time to let the user know whats going on.
    #TODO We should restart the game after an update.
    def completeupdate(self, msg, time):
        timer = celTimer(self.entity)
        timer.WakeUp(time, False)
        self.label.text = msg
        self.menu.clear()
        self.dl.running = False
        
    #Now we really leave
    def pctimer_wakeup(self, pc, args):
        timer = celTimer(self.entity)
        timer.Clear()
        RemoveEntity(self.entity)
            
    def scroller_down(self, pc, args):
        if self.desc:
            self.desc.scrolldown()
        
    def scroller_up(self, pc, args):
        if self.desc:
            self.desc.scrollup()
        
    def destruct(self, pc, args):
        ioDataBin.Store('updateskipped', self.updateskipped)
        self.killdescwindow()
        self.menu.clear()
        self.entity.PropertyClassList.RemoveAll()
        ioinit = Entities['ioInit']
        ioinit.Behaviour.SendMessage('updatecomplete', None, celGenericParameterBlock(0))
