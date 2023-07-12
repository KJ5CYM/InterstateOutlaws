from pycel import *
import os

import Menu
import ioInit
import ioLoader
import ioDataBin

class ioMainMenu:
    api_version = 2
    #The main menu
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']

        bg = celCreateBillboard(pl, self.entity)
        bg.materialnamefast = 'menu_bg'
        bg.x = 0
        bg.y = 0
        bg.width = 307200
        bg.height = 307200

        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
        
        self.menu = Menu.ioMenu(self.entity)
        xs = 21000
        ys = 16000
        melee = celBillboard(self.menu.addElement('', 'Melee_click', [0, 0], [xs, ys], 18, 'melee'))
        #Don't let them play multi melee if they haven't updated
        if ioDataBin.Get('updateskipped'):
            mmat = ''
        else:
            mmat = 'multimelee'
        multi = celBillboard(self.menu.addElement('', 'MultiMelee_click', [0, 0], [int(xs * 1.35), int(ys * 1.45)], 18, mmat))
        self.menu.addElement('', 'Garage_click', [0, 0], [xs, ys], 18, 'garage')
        self.menu.addElement('', 'Options_click', [0, 0], [xs, ys], 18, 'options')
        self.menu.addElement('', 'Credits_click', [0, 0], [xs, ys], 18, 'credits')
        exitgame = celBillboard(self.menu.addElement('', 'ExitGame_click', [0, 0], [xs, ys], 18, 'exit'))
        self.menu.align([80000, 135000], [3000, 3200])
        
        #Finetuning of menu
        multi.x = melee.x + 750
        multi.y = melee.y - 3500
        exitgame.x += 20000
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass

    def Melee_click(self, pc, args):
        #Set the properties on the databin so the hostgame screen knows
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        #Set the properties on the databin so the hostgame screen knows
        ioDataBin.Store('mpgame', False)
        hg = CreateEntity('ioHostGame', self.blpython, 'ioHostGame')
        RemoveEntity(self.entity)

    def MultiMelee_click(self, pc, args):
        #Set the properties on the databin so the hostgame screen knows
        ioDataBin.Store('mpgame', True)
        CreateEntity('ioServerSelect', self.blpython, 'ioServerSelect')
        RemoveEntity(self.entity)
        
    def Garage_click(self, pc, args):
        #Now the garage knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        garage = CreateEntity('ioGarage', self.blpython, 'ioGarage')
        RemoveEntity(self.entity)
        
    def Options_click(self, pc, args):
        options = CreateEntity('ioOptionsScreen', self.blpython, 'ioOptionsScreen')
        RemoveEntity(self.entity)
        
    def ExitGame_click(self, pc, args):
        ioInit.exitgame()

    def destruct(self, pc, args):
        self.menu.clear()
        self.entity.PropertyClassList.RemoveAll()