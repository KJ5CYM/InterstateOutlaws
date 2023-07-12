from pycel import *
import cPickle
#This behaviour holds  to store data between entities. It is used especially by the menus.
# It optionally stores its values pickled. It is only to be used with the helper functions

def Store (key, data, pickle = False):
    databin = pl.FindEntity('ioDataBin')
    if not databin:
        databin = CreateEntity('ioDataBin', BehaviourLayers['blpython'], 'ioDataBin')
    if pickle:
        data = cPickle.dumps(data, 0)
    pars = parblock({'key' : key, 'value' : data})
    databin.Behaviour.SendMessage('setdata', None, pars)
    
def Get(key, unpickle = False):
    databin = pl.FindEntity('ioDataBin')
    if not databin:
        databin = CreateEntity('ioDataBin', BehaviourLayers['blpython'], 'ioDataBin')
    pars = parblock({'key' : key})
    data = databin.Behaviour.SendMessage('getdata', None, pars)
    if unpickle:
        data = cPickle.loads(data)
    return data

class ioDataBin:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.data = {}
        
    def getdata(self, pc, args):
        key = args[parid('key')]
        return self.data[key]
    
    def setdata(self, pc, args):
        key = args[parid('key')]
        value = args[parid('value')]
        self.data[key] = value