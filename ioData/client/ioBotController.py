from pycel import *
class ioBotController:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        timer = celTimer(self.entity)
        timer.WakeUp(200, True)
        self.bot = None
        self.targetent = None
        self.targetname = ''
        self.accelerating = False
        self.shooting = False
        self.steering = 0
    
    #Set the bot with which we are to control
    def setcontrol(self, pc, args):
        self.bot = args[parid('entity')]
        self.botmesh = celMesh(self.bot)
        
    #The bot has changed targets
    def settarget(self, pc, args):
        self.targetname = args[parid('name')]
        self.targetent = Entities[self.targetname]
        if self.targetent:
            self.targetmesh = celMesh(self.targetent)
            
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()

    def pctimer_wakeup(self, pc, args):
        if self.bot:
            #Start accelerating if we arent already
            if not self.accelerating:
                self.bot.Behaviour.SendMessage('pccommandinput_accelerate1', None, args)
                self.accelerating = True
            #Try to pick a target
            if self.targetname == '':
                self.bot.Behaviour.SendMessage('pccommandinput_target1', None, args)
            else:
                if self.targetent:
                    targetpos = self.targetmesh.Mesh.GetMovable().GetPosition()
                    reltargetpos = self.botmesh.Mesh.GetMovable().GetTransform().Other2This(targetpos)
                    if reltargetpos.x > 0:
                        if self.steering != -1:
                            self.bot.Behaviour.SendMessage('pccommandinput_steerleft1', None, args)
                            self.steering = -1
                    else:
                        if self.steering != 1:
                            self.bot.Behaviour.SendMessage('pccommandinput_steerright1', None, args)
                            self.steering = 1
            #Fire in bursts:
            if not self.shooting:
                self.bot.Behaviour.SendMessage('pccommandinput_shoot1', None, args)
                self.shooting = True
            else:
                self.bot.Behaviour.SendMessage('pccommandinput_shoot0', None, args)
                self.shooting = False