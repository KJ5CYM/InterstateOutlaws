from pycel import *
import random

import Menu
import ioDataBin
import ioLoader
import ioNetworkEnt
import ioNetHelper
import ioScroller

#Handles miscellaneous network/gameplay stuff like chat and loading the map
class ioNetGameClient:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.playername = Config.GetStr('Outlaws.Player.Name')
        self.playerinp = None
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.client = Entities['ioCl']
        self.mapname = ''
        self.frames = 0
        self.net = ioNetHelper.ioNetHelper()
        
        self.menu = Menu.ioMenu(self.entity)
        timsg = 'textinput_clicked'
        tipos = (55000, 234000)
        tisize = (150000, 8000)
        tifsize = Menu.GetFontConstant()
        self.textinput = self.menu.addElement('ioChatLine', timsg, tipos, tisize, tifsize, 'unselection', 'ioTextInput')
        self.msgbb = celBillboard(self.textinput)
        
        #Allow the player to hide the hud by pressing a key
        hudbind = Config.GetStr('Outlaws.Keys.HUD.Hide', 'h')
        #Allow the player to enter chat mode by pressing a key
        chatbind = Config.GetStr('Outlaws.Keys.Message.Start', 'lalt')
        pcinput = celCommandInput(self.entity)
        pcinput.Bind(chatbind, 'chat')
        pcinput.Bind(hudbind, 'hidehud')
        
        self.visible = False
        self.logs = None
        
    def setvisible(self, pc, args):
        self.visible = args[parid('visible')]
        if self.visible:
            self.logsbb = celAddBillboard(self.entity)
            self.logsbb.materialnamefast = 'half-black'
            self.logsbb.x = 0
            self.logsbb.y = 0
            self.logsbb.width = 175000
            self.logsbb.height = 40000
            self.logs = ioScroller.ioScroller(self.entity, [0, 0], [self.logsbb.width, self.logsbb.height], 'logs')
            self.logs.allowdoubles = True
        else:
            self.logs.destruct()
            self.logs = None
        
    def pccommandinput_chat1(self, pc, args):
        #Don't do this unless we are active
        if self.menu.active != self.textinput:
            #Try to get player's commandinput, so it doesnt respond while we type
            if not self.playerinp:
                player = Entities[self.playername]
                if player:
                    self.playerinp = celCommandInput(player)
            if self.playerinp:
                self.playerinp.Activate(False)
            self.msgbb.materialnamefast = 'half-black'
            #self.textinput.Behaviour.SendMessage('skipnext', None, celGenericParameterBlock(0))
            self.menu.activate('ioChatLine')
            celBillboard(self.textinput).text = 'Say something...'

    #Hide the hud
    def pccommandinput_hidehud1(self, pc, args):
        #Not if the game menu is open though, or we are chatting
        gamemenu = Entities['ioGameMenu']
        if not gamemenu and self.menu.active != self.textinput:
            hud = Entities['ioHUD']
            hudvisible = hud.Behaviour.SendMessage('getvisible', None, celGenericParameterBlock(0))
            
            pars = parblock({'visible' : not hudvisible})
            hud.Behaviour.SendMessage('setvisible', None, pars)
    
    #User pressed enter, send their message
    def textinput_enter(self, pc, args):
        if self.playerinp:
            self.playerinp.Activate(True)
        self.menu.deactivateAll()
        msg = self.msgbb.text
        if not msg:
            msg = ''
        self.net.sendData('ioGSrv', 'msg', [msg])
        self.msgbb.materialnamefast = 'unselection'
        self.textinput.Behaviour.SendMessage('clear', None, celGenericParameterBlock(0))
        
    #A user sent a chat message. Forward it onto the gametype for display
    def r_msg(self, pc, args):
        addr, data = self.net.getNetData(args)
        msg = ': '.join(data)
        self.logEvent(msg)
        
    def setmapname(self, pc, args):
        self.mapname = args[getid('cel.parameter.name')]
        #A delay hack to ensure the server screen gets to update before the blocking loader loads.
        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(0)

    def pctimer_wakeupframe(self, pc, args):
        self.frames += 1
        if self.frames == 3 :
            self.frames = 0
            self.timer.Clear()
            mapinfo = ioLoader.findSubfolderCfgString('maps', self.mapname)
            ioLoader.loadLibraryFolder('effects')
            ioLoader.loadWorldFolder('weapons', True)
            ioLoader.loadWorldFolder('vehicles', True)
            ioLoader.loadWorldFolder('entities', True)
            gameworld = ioLoader.makeGameWorld(mapinfo['Path'])
            Engine.PrecacheDraw()
            zonemgr = celZoneManager(gameworld)
            start = zonemgr.GetLastStartName()
            cam = celDefaultCamera(gameworld)
            cam.PointCamera(start)
            pars = celGenericParameterBlock(0)
            self.serverscr = Entities['ioServerScreen']
            self.serverscr.Behaviour.SendMessage('maploaded', None, pars)
            self.client.Behaviour.SendMessage('maploaded', None, pars)
            
            self.buttons = Menu.ioMenu(self.entity)
            self.buttons.addElement('Play', 'Play_click', [135000, 242500], [20000, 10000], self.fconst, 'button-bg')
            #Not implemented yet
            #self.buttons.addElement('Spectate', 'Spectate_click', [155000, 242500], [30000, 10000], self.fconst, 'button-bg')
    
            self.net.sendData('ioEntMgr', 'fillents', [], None)
            
            if not ioDataBin.Get('mpgame'):
                #Used for debugging damage system
                entmgr = Entities['ioEntMgrCl']
                #entmgr.Behaviour.SendMessage('fillbots', None, args)

    def Play_click(self, pc, args):
        self.buttons.clear()
        RemoveEntity(self.serverscr)
        CreateEntity('ioHUD', self.blpython, 'ioHUD')
        entmgr = Entities['ioEntMgrCl']
        entmgr.Behaviour.SendMessage('makeplayer', None, args)
        gmtp = Entities['ioGmTpCl']
        pars = parblock({'visible' : True})
        gmtp.Behaviour.SendMessage('setvisible', None, pars)
        self.entity.Behaviour.SendMessage('setvisible', None, pars)

    def Spectate_click(self, pc, args):
        self.buttons.clear()
        RemoveEntity(self.serverscr)
        entmgr = Entities['ioEntMgrCl']
        entmgr.Behaviour.SendMessage('makespectator', None, celGenericParameterBlock(0))
        gmtp = Entities['ioGmTpCl']
        pars = parblock({'visible' : True})
        gmtp.Behaviour.SendMessage('setvisible', None, pars)
        self.entity.Behaviour.SendMessage('setvisible', None, pars)

    def leavegame(self, pc, args):
        hud = Entities['ioHUD']
        if hud:
            RemoveEntity(hud)
        gametype = Entities['ioGmTpCl']
        if gametype:
            RemoveEntity(gametype)
        entmgr = Entities['ioEntMgrCl']
        if entmgr:
            RemoveEntity(entmgr)
        client = Entities['ioCl']
        if client:
            RemoveEntity(client)
        ioLoader.unloadGameWorld()
        RemoveEntity(self.entity)

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.menu.clear()
        if self.logs:
            self.logs.destruct()
        
    #Log an event. Usually someone died
    def logEvent(self, event):
        if self.logs:
            self.logs.additem(event, 'log')
            if len(self.logs.items) > self.logs.getmaxvisible():
                self.logs.scrolldown()
        
    #Log a message. This function is a message to be used by other entities
    def logevent(self, pc, args):
        message = args[parid('message')]
        self.logEvent(message)