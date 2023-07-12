from pycel import *
import cPickle

from ioStatsBase import *
import ioLoader
import Menu
import ioScroller
import ioDataBin

#DM gameover screen
class ioDmStats (ioStatsBase):
    api_version = 2
    
    #The server interaction screen
    def __init__(self,celEntity):
        ioStatsBase.__init__(self, celEntity)
        self.names = Menu.ioMenu(self.entity)
        self.scores = Menu.ioMenu(self.entity)
            
    def fillstats(self, pc, args):
        stats = cPickle.loads(args[parid('stats')])
        items = [(data[0], name) for name, data in stats.iteritems()]
        sortedplayers = sorted(items, reverse = True)
        for score, name in sortedplayers:
            bb = celAddBillboard(self.entity)
            self.names.addElement(name, '', (0, 0), (0, 0), Menu.GetFontConstant(), '')
            self.scores.addElement(str(score), '', (0, 0), (0, 0), Menu.GetFontConstant(), '')
        self.names.align((50000, 60000), (0, 15000))
        self.scores.align((150000, 60000), (0, 15000))
        
    def destruct(self, pc, args):
        ioStatsBase.destruct(self, pc, args)
        self.names.clear()
        self.scores.clear()
            