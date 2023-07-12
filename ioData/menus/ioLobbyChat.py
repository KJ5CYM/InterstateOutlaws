from pycel import *
import cPickle

import ioNetHelper
import ioDataBin
import ioScroller
import Menu

#Handles the chatroom in the lobby
class ioLobbyChat:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.net = ioNetHelper.ioNetHelper()
        lobbyname, self.lobbyserver = ioDataBin.Get('lobbyserver', True)
        #The list of messages on the left
        self.msgscroller = ioScroller.ioScroller(self.entity, (43000, 196000), (163900, 57500), '_msg')
        #The list of clients on the right
        self.namescroller = ioScroller.ioScroller(self.entity, (211000, 196000), (47500, 57500), '_names')
        self.msgscroller.allowdoubles = True
        self.menu = Menu.ioMenu(self.entity)
        timsg = 'textinput_clicked'
        tipos = (43000, 254000)
        tisize = (207000, 8000)
        tifsize = Menu.GetFontConstant()
        self.textinput = self.menu.addElement('ioChatLine', timsg, tipos, tisize, tifsize, 'unselection', 'ioTextInput') 
        self.menu.activate('ioChatLine')
    
    def scroller_up_names(self, pc, args):
        self.namescroller.scrollup()
        
    def scroller_down_names(self, pc, args):
        self.namescroller.scrolldown()
    
    def scroller_up_msg(self, pc, args):
        self.msgscroller.scrollup()
        
    def scroller_down_msg(self, pc, args):
        self.msgscroller.scrolldown()
    
    #We have joined the chat server
    def joined(self, pc, args):
        self.net.sendData('ioLS', 'getclientnames', [self.entity.Name], self.lobbyserver)
        
    #user pressed enter, send the message
    def textinput_enter(self, pc, args):
        self.menu.activate('')
        msg = celBillboard(self.textinput).text
        self.net.sendData('ioLS', 'msg', [msg], self.lobbyserver)
        self.textinput.Behaviour.SendMessage('clear', None, celGenericParameterBlock(0))
        self.menu.activate('ioChatLine')

    #We got a chat message
    def r_msg(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.msgscroller.additem(': '.join(data), '')
        if len(self.msgscroller.items) > self.msgscroller.getmaxvisible():
            self.msgscroller.scrolldown()

    #Someone has joined the lobby.
    def r_addclient(self, pc, args):
        addr, data = self.net.getNetData(args)
        name = data[0]
        self.namescroller.additem(name, '')
        
    def destruct(self, pc, args):
        self.msgscroller.destruct()
        self.namescroller.destruct()
        self.menu.clear()