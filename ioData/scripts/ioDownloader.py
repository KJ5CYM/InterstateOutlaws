from pycel import *

import urllib2
import threading
import time

#Utility function. The main thread calls this every frame to dispatch
#messages in the downloaders event que
def dispatch(owner, downloader):
    while len(downloader.events) > 0:
            event = downloader.events.pop(0)
            message = event[0]
            pars = event[1]
            func = getattr(owner, message) 
            func(pars)

class ioDownloader(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.running = False
        self.data = ''
        self.chunk = 1024
        self.read = 0
        self.size = 1
        self.lastread = 1
        self.dead = False
        #Our event que
        self.events = []
        try:
            self.remotefile = urllib2.urlopen(url)
        except (urllib2.HTTPError, urllib2.URLError, ValueError), error:
            self.events.append(('downloader_error', [error]))
            self.dead = True
        except:
            self.events.append(('downloader_error', ['Unknown / Unhandled']))
            self.dead = True
        if not self.dead:
            info = self.remotefile.info()
            try:
                self.size = int(info['Content-Length'])
                self.nolength = False
            except KeyError:
                self.nolength = True
        
    def run(self):
        self.running = True
        finished = False
        while self.running and not finished and not self.dead:
            data = self.remotefile.read(self.chunk)
            self.lastread = len(data)
            self.data += data
            self.read += self.chunk
            self.events.append(('downloader_read', []))
            if self.nolength:
                finished = (self.lastread > 0)
            else:
                finished = (self.read >= self.size)
        if finished:
            self.events.append(('downloader_complete', []))
