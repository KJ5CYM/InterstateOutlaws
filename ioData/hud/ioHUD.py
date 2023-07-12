from pycel import *
import cPickle
import Menu
import socket

class ioHUD:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.playername = Config.GetStr('Outlaws.Player.Name')
        self.visible = True
        self.xpos = 195840
        self.ypos = 0
        self.player = None
        self.playermech = None
        self.playermesh = None
        self.playerwheeled = None
        self.weapons = {}
        self.hardpoints = []
        self.fconst = Menu.GetFontConstant()
        Vfs.ChDir('/outlaws/hud')
        Loader.LoadMapFile('/outlaws/hud/world', False)

        self.reticles = []
        
        self.bg = celAddBillboard(self.entity)
        self.bg.materialnamefast = 'hud_back'
        self.bg.x = self.xpos
        self.bg.y =  self.ypos
        self.bg.width = 111360
        self.bg.height = 97280
        
        self.speedo = celAddBillboard(self.entity)
        self.speedo.materialnamefast = 'speedo'
        self.speedo.x = 230400
        self.speedo.y = 232192
        self.speedo.width = 70272
        self.speedo.height = 92160
    
        self.needle = celAddBillboard(self.entity)
        self.needle.materialnamefast = 'needle'
        self.needle.x = 237312
        self.needle.y = 246784
        self.needle.width = 55000
        self.needle.height = 65000
        
        #We average the last 10 gathered speeds to smooth out the needle
        self.speeds = []
        
        self.gear = celAddBillboard(self.entity)
        self.gear.x = 170000
        self.gear.y = 280000
        self.gear.width = 55000
        self.gear.height = 25000
        self.gear.materialnamefast = 'gear-d'
        
        self.gtext = celAddBillboard(self.entity)
        self.gtext.x = 220000
        self.gtext.y = 295000
        self.gtext.text_font_size = self.fconst
        self.gtext.text_font = '/outlaws/fonts/lcd2.ttf'
        self.gtext.text_fg_color = csColor(1, 1, 1)

        self.wsyslabel = celAddBillboard(self.entity)
        self.wsyslabel.x = self.xpos + 9600
        self.wsyslabel.y = self.ypos + 15104
        self.wsyslabel.text_font_size = self.fconst * 0.9
        self.wsyslabel.text_font = '/outlaws/fonts/lcd2.ttf'
        self.wsyslabel.text_fg_color = Menu.GetFontColor()
        self.wsyslabel.text = 'o Weapons'
        
        self.vsyslabel = celAddBillboard(self.entity)
        self.vsyslabel.x = self.xpos + 9600
        self.vsyslabel.y = self.ypos + 58112
        self.vsyslabel.text_font_size = self.fconst * 0.9
        self.vsyslabel.text_font = '/outlaws/fonts/lcd2.ttf'
        self.vsyslabel.text_fg_color = Menu.GetFontColor()
        self.vsyslabel.text = 'o Systems'

        self.setupwheeldisplays()
        self.setuppowertraindisplay()
        self.setupframedisplays()
        self.setuparmourdisplays()
    
        timer = celTimer(self.entity)
        timer.WakeUpFrame(True)
        
        timer.WakeUp(50, True)

        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'gamemenu')
        
        self.lagicon = None
        self.targetent = None
        self.targetmesh = None
        self.camera = None
        gameworld = Entities['ioGameWorld']
        if gameworld:
            self.camera = celDefaultCamera(gameworld).GetCamera()

    def addweapon(self, pc, args):
        name = args[parid('name')]
        if not self.weapons.has_key(name):
            bb = celAddBillboard(self.entity)
            plusy = 21104 + len(self.weapons) * 5000
            bb.x = self.xpos + 9600
            bb.y = self.ypos + plusy
            bb.width = 50000
            bb.height = 5000
            bb.text_font_size = self.fconst * 0.9
            bb.text_font = '/outlaws/fonts/lcd2.ttf'
            bb.text_fg_color = Menu.GetFontColor()
            bb.clickable = True
            bb.materialnamefast = 'unselection'
            self.weapons[name] = bb
            self.hardpoints.append(bb)
            #We check this when it is clicked
            bb.Tag = str(len(self.hardpoints))
            
    #Hmm, this only currently supports four wheels. It should be able to do more.
    def setupwheeldisplays(self):
        self.wheels = []
        for i in xrange(4):
            bb = celAddBillboard(self.entity)
            bb.materialnamefast = 'wheel-op'
            bb.width = 4416
            bb.height = 11264
            self.wheels.append(bb)
        self.wheels[0].x = self.xpos + 72784
        self.wheels[0].y = self.ypos + 23040
        self.wheels[1].x = self.xpos + 93904
        self.wheels[1].y = self.ypos + 23040
        self.wheels[2].x = self.xpos + 72784
        self.wheels[2].y = self.ypos + 64512
        self.wheels[3].x = self.xpos + 93904
        self.wheels[3].y = self.ypos + 64512
        
        self.brlabel = celAddBillboard(self.entity)
        self.brlabel.x = self.xpos + 9600
        self.brlabel.y = self.ypos + 69112
        self.brlabel.text_font_size = self.fconst * 0.9
        self.brlabel.text_font = '/outlaws/fonts/lcd2.ttf'
        self.brlabel.text_fg_color = Menu.GetFontColor()
        self.brlabel.text = 'o BRAKES'
        
    def setuppowertraindisplay(self):
        self.pt = celAddBillboard(self.entity)
        self.pt = self.pt
        self.pt.materialnamefast = 'pt-op'
        self.pt.x = self.xpos + 76608
        self.pt.y = self.ypos + 24320
        self.pt.width = 17664
        self.pt.height = 49152
        
        self.ptlabel = celAddBillboard(self.entity)
        self.ptlabel.x = self.xpos + 9600
        self.ptlabel.y = self.ypos + 64112
        self.ptlabel.text_font_size = self.fconst * 0.9
        self.ptlabel.text_font = '/outlaws/fonts/lcd2.ttf'
        self.ptlabel.text_fg_color = Menu.GetFontColor()
        self.ptlabel.text = 'o POWERTRAIN'
        
    def setupframedisplays(self):
        front = celAddBillboard(self.entity)
        front.materialnamefast = 'sus-front-op'
        front.x = self.xpos + 77184
        front.y = self.ypos + 19968
        front.width = 16320
        front.height = 14592
        
        rear = celAddBillboard(self.entity)
        rear.materialnamefast = 'sus-rear-op'
        rear.x = self.xpos + 78336
        rear.y = self.ypos + 62464
        rear.width = 14208
        rear.height = 12288
        
        left = celAddBillboard(self.entity)
        left.materialnamefast = 'sus-left-op'
        left.x = self.xpos + 76224
        left.y = self.ypos + 36352
        left.width = 4032
        left.height = 24831
        
        right = celAddBillboard(self.entity)
        right.materialnamefast = 'sus-right-op'
        right.x = self.xpos + 90432
        right.y = self.ypos + 36352
        right.width = 4032
        right.height = 24831
        
        self.frame = [front, rear, left, right]
        
        self.framelabel = celAddBillboard(self.entity)
        self.framelabel.x = self.xpos + 9600
        self.framelabel.y = self.ypos + 74112
        self.framelabel.text_font_size = self.fconst * 0.9
        self.framelabel.text_font = '/outlaws/fonts/lcd2.ttf'
        self.framelabel.text_fg_color = Menu.GetFontColor()
        self.framelabel.text = 'o SUS/FRAME'
    
    #Display armour status in the black part
    def setuparmourdisplays(self):
        front = celAddBillboard(self.entity)
        front.materialnamefast = 'armour-front-op'
        front.x = self.xpos + 72960
        front.y = self.ypos + 14824
        front.width = 24000
        front.height = 5376
        
        rear = celAddBillboard(self.entity)
        rear.materialnamefast = 'armour-rear-op'
        rear.x = self.xpos + 72960
        rear.y = self.ypos + 76824
        rear.width = 24000
        rear.height = 5888
        
        left = celAddBillboard(self.entity)
        left.materialnamefast = 'armour-side-op'
        left.x = self.xpos + 72960
        left.y = self.ypos + 35328
        left.width = 1152
        left.height = 28672
        
        right = celAddBillboard(self.entity)
        right.materialnamefast = 'armour-side-op'
        right.x = self.xpos + 96768
        right.y = self.ypos + 35328
        right.width = 1152
        right.height = 28672
        
        self.armour = [front, rear, left, right]
        
    def setweapon(self, pc, args):
        codename = args[parid('codename')]
        name = args[parid('name')]
        status = args[parid('status')]
        ammo = args[parid('ammo')]
        
        display = self.weapons[name]
        sammo = str(int(ammo))
        dots = '.' * (20 - len(codename) - len(sammo))
        dispstring = '%s%s%s%s' % (status, codename, dots, sammo)
        display.text = dispstring
        
    def setwheel(self, pc, args):
        index = int(args[parid('index')])
        armour = args[parid('armour')]
        states = ['wheel-fail', 'wheel-critical', 'wheel-severe', 'wheel-light', 'wheel-op']
        state = int(round(armour / 33.33))
        if index < 4:
            self.wheels[index].materialnamefast = states[state]
            
    def setarmour(self, pc, args):
        index = int(args[parid('index')])
        armour = args[parid('armour')]
        mats = ['armour-front', 'armour-rear', 'armour-side', 'armour-side']
        states = ['-fail', '-critical', '-severe', '-light', '-op']
        state = int(round(armour/ 25.0))
        mat = '%s%s' % (mats[index], states[state])
        self.armour[index].materialnamefast = mat
        
    def sethealth(self, pc, args):
        health = args[parid('health')]
        state = int(round(health / 50.0))
        append = ''
        if state is 0:
            append = ' - Critical!'
        if state is 1:
            append = ' - Damaged'
        if health <= 0:
            append = ' - Offline'
        text = '%s Systems%s' % (['x', '!', 'o'][state], append)
        self.vsyslabel.text = text
        
    def setframe(self, pc, args):
        index = int(args[parid('index')])
        frame = args[parid('frame')]
        average = args[parid('average')]
        mats = ['sus-front', 'sus-rear', 'sus-left', 'sus-right']
        states = ['-fail', '-critical', '-severe', '-light', '-op']
        state = int(round(frame / 25.0))
        mat = '%s%s' % (mats[index], states[state])
        self.frame[index].materialnamefast = mat
        labelstate = int(round(average / 50.0))
        self.framelabel.text = '%s SUS/FRAME' % ['x', '!', 'o'][labelstate]
        
    def setpowertrain(self, pc, args):
        powertrain = args[parid('powertrain')]
        states = ['pt-fail', 'pt-critical', 'pt-severe', 'pt-light', 'pt-op']
        state = int(round(powertrain / 12.5))
        self.pt.materialnamefast = states[state]
        ptstate = int(round(powertrain / 25.0))
        self.ptlabel.text = '%s POWERTRAIN' % ['x', '!', 'o'][ptstate]

    def setbrakes(self, pc, args):
        brakes = args[parid('brakes')]
        brakesstate = int(round(brakes / 25.0))
        self.brlabel.text = '%s BRAKES' % ['x', '!', 'o'][brakesstate]
    
    #Totally kill all displays
    def alldie(self, pc, args):
        self.framelabel.text = 'x SUS/FRAME'
        self.ptlabel.text = 'x POWERTRAIN'
        self.pt.materialnamefast = 'pt-fail'
        self.brlabel.text = 'x BRAKES'
        sides = ['front', 'rear', 'side', 'side']
        for i, side in enumerate(sides):
            self.armour[i].materialnamefast = 'armour-%s-fail' % side
            self.frame[i].materialnamefast = 'sus-%s-fail' % side
            #A little hack.
            self.wheels[i].materialnamefast = 'wheel-fail'
        sides = ['front', 'rear', 'left', 'right']
        for i, side in enumerate(sides):
            self.frame[i].materialnamefast = 'sus-%s-fail' % side
        for i in xrange(4):
            self.wheels[i].materialnamefast = 'wheel-fail'
        self.vsyslabel.text = 'x Systems - Offline'
            
    #Totally restore all displays
    def allrestore(self, pc, args):
        self.framelabel.text = 'o SUS/FRAME'
        self.ptlabel.text = 'o POWERTRAIN'
        self.pt.materialnamefast = 'pt-op'
        self.brlabel.text = 'o BRAKES'
        sides = ['front', 'rear', 'side', 'side']
        for i, side in enumerate(sides):
            self.armour[i].materialnamefast = 'armour-%s-op' % side
            #A little hack.
            self.wheels[i].materialnamefast = 'wheel-op'
        sides = ['front', 'rear', 'left', 'right']
        for i, side in enumerate(sides):
            self.frame[i].materialnamefast = 'sus-%s-op' % side
        for i in xrange(4):
            self.wheels[i].materialnamefast = 'wheel-op'
        self.vsyslabel.text = 'o Systems'

    #Update the speedo needle
    def pctimer_wakeup(self, pc, args):
        if self.playermech:
            #We should be multiplying by 3.6. but 7.2 makes the car look twice as fast :)
            speed = self.playermech.Body.GetLinearVelocity().Norm() * 3.6
            self.speeds.append(speed)
            if len(self.speeds) > 10:
                self.speeds.pop(0)
            avgspeed = sum(self.speeds) / 10
            self.needle.Billboard.SetRotation(avgspeed/80)

    #Check if we can pick up the player, and try to get its speed for the needle. and gear, aimer etc.
    def pctimer_wakeupframe(self, pc, args):
        #Check for player
        if not self.player:
            player = Entities[self.playername]
            if player:
                self.playermech = celMechanicsObject(player)
                self.playerwheeled = celWheeled(player)
                self.player = player
                self.playermesh = celMesh(player)
            
        #Update gear display
        if self.playerwheeled:
            gear = self.playerwheeled.Gear
            if gear > 0:
                gmat = 'gear-d'
                self.gtext.text = str(gear)
            elif gear == 0:
                gmat = 'gear-n'
                self.gtext.text = ''
            elif gear == -1:
                gmat = 'gear-r'
                self.gtext.text = ''
            self.gear.materialnamefast = gmat
            
        #Update the aiming reticle position
        if self.targetmesh and self.camera and (self.reticles != []):
            show = True
            screenbb = self.targetmesh.Mesh.GetScreenBoundingBox(self.camera)
            if screenbb.distance == -1.0:
                show = False
            sbox = screenbb.sbox
            sw = Graphics2D.GetWidth()
            sh = Graphics2D.GetHeight()
            xconst = 307200 / sw
            yconst = 307200 / sh
            xpos = sbox.MinX()
            ypos = sh - sbox.MaxY()
            margin = 2000
            xsize = int(sbox.MaxX() - sbox.MinX()) * xconst + (margin * 2)
            ysize = int(sbox.MaxY() - sbox.MinY()) * yconst + (margin * 2)
            xleft = int(xpos * xconst) - margin
            xright = xleft + xsize - (margin / 2)
            ytop = int(ypos * yconst) - margin
            ybottom = ytop + ysize - (margin / 2)
            xcentre = int((xleft + xright) / 2)
            ycentre = int((ytop + ybottom) / 2)
            halfxsize = int(xsize / 2)
            halfysize = int(ysize / 2)
            
            #Don't show if it starts dominating the screen
            dominatingsize = 200000
            if (halfxsize > dominatingsize) or (halfysize > dominatingsize):
                show = False

            #Loop through all 5 reticles, updating their position in formation, and colour
            names = ['bar', 'front', 'rear', 'left', 'right']
            for i, ret in enumerate(self.reticles):
                name = names[i]
                if name is 'bar':
                    ret.height = 2000
                    ret.x = xleft
                    ret.y = ytop - 2000
                    armour = self.targetent.Behaviour.SendMessage('gethealth', None, celGenericParameterBlock(0))
                    ret.width = int((armour / 100) * xsize)
                    mat = 'armour-bar'
                else:
                    if name is 'front':
                        ret.width = xsize
                        ret.height = 2000
                        ret.x = xleft
                        ret.y = ytop
                        mat = 'armour-bar'
                    elif name is 'rear':
                        ret.width = xsize
                        ret.height = 2000
                        ret.x = xleft
                        ret.y = ybottom
                        mat = 'armour-bar'
                    elif name is 'left':
                        ret.width = 1500
                        ret.height = ysize
                        ret.x = xleft
                        ret.y = ytop
                        mat = 'armour-side'
                    elif name is 'right':
                        ret.width = 1500
                        ret.height = ysize
                        ret.x = xright
                        ret.y = ytop
                        mat = 'armour-side'
                    pars = parblock({'index' : i - 1})
                    armour = self.targetent.Behaviour.SendMessage('getarmour', None, pars)
                idx = int(round(armour / 25.0))
                states = ['-fail', '-critical', '-severe', '-light', '-op']
                ret.materialnamefast = '%s%s' % (mat, states[idx])
            #If the target is offscreen dissapear.
            if not show:
                for ret in self.reticles:
                    ret.materialnamefast = ''

    def pccommandinput_gamemenu1(self, pc, args):
        gm = pl.FindEntity('ioGameMenu')
        if not gm:
            CreateEntity('ioGameMenu', self.blpython, 'ioGameMenu')

    def pccommandinput_gamemenu_(self, pc, args):
        pass
        
    def pccommandinput_gamemenu0(self, pc, args):
        pass

    #Player has picked a new target.
    def settarget(self, pc, args):
        targetname = args[parid('name')]
        if targetname != '' and targetname != None:
            self.targetent = Entities[targetname]
            if self.targetent:
                self.targetmesh = celGetMesh(self.targetent)
                #Create our reticles
                if self.reticles == []:
                    for retname in ['bar', 'front', 'rear', 'side', 'side']:
                        ret = celAddBillboard(self.entity)
                        ret.x = 0
                        ret.y = 0
                        ret.width = 0
                        ret.height = 0
                        self.reticles.append(ret)
        else:
            self.targetent = None
            self.targetmesh = None
        if not self.targetent:
            for ret in self.reticles:
                self.entity.PropertyClassList.Remove(ret)
            
    #Player has chosen a new linked weapon group. Update our display
    def setlink(self, pc, args):
        group = cPickle.loads(args[parid('group')])
        for hardpoint in self.hardpoints:
            hardpoint.materialnamefast = 'unselection'
        #First deselect all
        for i in group:
            self.hardpoints[i - 1].materialnamefast = 'selection'
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        
    #Hide or show the hud
    def setvisible(self, pc, args):
        self.visible = args[parid('visible')]
        self.bg.visible = self.visible
        self.speedo.visible = self.visible
        self.needle.visible = self.visible
        self.gear.visible = self.visible
        self.gtext.visible = self.visible
        self.wsyslabel.visible = self.visible
        self.vsyslabel.visible = self.visible
        self.brlabel.visible = self.visible
        self.ptlabel.visible = self.visible
        self.pt.visible = self.visible
        self.framelabel.visible = self.visible
        bbs = self.weapons.values()
        bbs += self.wheels
        bbs += self.armour
        bbs += self.frame
        bbs += self.reticles
        for bb in bbs:
            bb.visible = self.visible
    
    def getvisible(self, pc, args):
        return self.visible
    
    #Hopefully they clicked on a weapon. Then toggle it from our group, and tell the player vehicle.
    def pcbillboard_select(self, pc, args):
        if self.player is not None:
            try:
                hardpoint = int(pc.Tag)
                pc = self.hardpoints[hardpoint - 1]
                pars = parblock({'hardpoint' : hardpoint})
                mat = pc.materialnamefast
                if mat == 'selection':
                    pc.materialnamefast = 'unselection'
                    message = 'removelink'
                else:
                    pc.materialnamefast = 'selection'
                    message = 'addlink'
                self.player.Behaviour.SendMessage(message, None, pars)
            except:
                pass

    #According to ioClient, server hasn't responded in a while
    def lag(self, pc, args):
        if not self.lagicon:
            self.lagicon = celAddBillboard(self.entity)
            self.lagicon.materialnamefast = 'networkbad'
            self.lagicon.width = 30000
            self.lagicon.height = 40000
            self.lagicon.x = 10000
            self.lagicon.y = 120000
            
    def unlag(self, pc, args):
        if self.lagicon:
            self.entity.PropertyClassList.Remove(self.lagicon)
            self.lagicon = None