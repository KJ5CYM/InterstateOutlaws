from pycel import *

class ioMapBase:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity

    def pcdynamicbody_collision(self, pc, args):
        pass

    def pcdamage_hurt(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()

