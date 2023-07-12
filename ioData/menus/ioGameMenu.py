from pycel import *
import Menu
import os

import ioLoader
import ioDataBin
import ioNetHelper

#The menu that is opened when the user presses esc ingame
class ioGameMenu:
    api_version = 2
    
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.net = ioNetHelper.ioNetHelper()

        self.bg = celCreateBillboard(pl, self.entity).Billboard
        self.bg.SetMaterialName('half-black')
        self.bg.SetPosition(0,0)
        self.bg.SetSize(307200,307200)

        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
        
        self.makeButtons()
        
        self.createdtime = Clock.GetCurrentTicks()
        
    def makeButtons(self):
        self.menu = Menu.ioMenu(self.entity)
        self.menu.addElement('Return to Game', 'Back_click', [0, 0], [60000,10000], self.fconst, 'button-bg')
        if ioDataBin.Get('mpgame'):
            self.menu.addElement('Return to Lobby', 'Lobby_click', [0, 0], [60000,10000], self.fconst, 'button-bg')
        self.menu.addElement('Exit to Menu', 'Menu_click', [0, 0], [60000,10000], self.fconst, 'button-bg')
        self.menu.addElement('Exit Interstate Outlaws', 'Exit_click', [0, 0], [60000,10000], self.fconst, 'button-bg')
        self.menu.align([80000, 130000], [0, 10000])
        
    def Back_click(self, pc, args):
        RemoveEntity(self.entity)
        
    def Lobby_click(self, pc, args):
        self.afterpoll = self.returntolobby
        self.pollserver()
        
    def Menu_click(self, pc, args):
        self.afterpoll = self.returntomenu
        self.pollserver()
    
    def Exit_click(self, pc, args):
        self.afterpoll = self.quitgame
        self.pollserver()

    def pccommandinput_exit1(self, pc, args):
        timediff = Clock.GetCurrentTicks() - self.createdtime
        if timediff > 1000:
            RemoveEntity(self.entity)

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.menu.clear()
        
    #Polls for a running game server. if found, asks user if they want to quit.
    #Then executes function self.afterpoll() after thats done
    def pollserver(self):
        self.serverfound = False
        self.net.sendData('ioGSrv', 'poll', [self.entity.Name])
        timer = celTimer(self.entity)
        timer.WakeUp(250, False)
        
    #Now ask the user if they want to quit the server if it exists
    def pctimer_wakeup(self, pc, args):
        if self.serverfound: 
            if ioDataBin.Get('mpgame'):
                self.menu.clear()
                label1 = 'You are currently hosting a game'
                label2 = 'Would you like to stop it?'
                self.menu.addElement(label1, '', [100000, 100000],  [0, 0], self.fconst, '')
                self.menu.addElement(label2, '', [100000, 110000],  [0, 0], self.fconst, '')
                self.menu.addElement('Yes', 'yes_click', [100000, 130000],  [15000, 10000], self.fconst, 'button-bg')
                self.menu.addElement('No', 'no_click', [120000, 130000],  [15000, 10000], self.fconst, 'button-bg')
            #If its a single player game just quit
            else:
                self.net.sendData('ioGSrv', 'quit', [])
                self.afterpoll()
        else:
            self.afterpoll()
     
    #The user wants to quit the server
    def yes_click(self, pc, args):
        self.net.sendData('ioGSrv', 'quit', [])
        self.afterpoll()
    
    #Just do the rest
    def no_click(self, pc, args):
        self.afterpoll()
        
    #There is a local server
    def r_pollreply(self, pc, args):
        self.serverfound = True
        
    def quitgame(self):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))
            
    def returntomenu(self):
        netgame = Entities['ioNetMgrCl']
        netgame.Behaviour.SendMessage('leavegame', None, celGenericParameterBlock(0))
        CreateEntity('ioMainMenu', self.blpython, 'ioMainMenu')
        RemoveEntity(self.entity)
        
    def returntolobby(self):
        netgame = Entities['ioNetMgrCl']
        netgame.Behaviour.SendMessage('leavegame', None, celGenericParameterBlock(0))
        CreateEntity('ioGameSelect', self.blpython, 'ioGameSelect')
        RemoveEntity(self.entity)