from pycel import *
import cPickle
import Menu
import ioLoader
import ioNetworkEntCl
import ioScroller
import ioDataBin
import os

class ioGarage:
    api_version = 2
    #The main menu
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']    
        #Make the splash screen while we load the garage
        self.splash = CreateEntity('ioSplashScreen', self.blpython, 'ioSplashScreen')
        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(2)
        self.frames = 0
        
    #Now we start loading, and delete the splash screen. it will clear when loading is finished
    def pctimer_wakeupframe(self, pc, args):
        self.frames += 1
        if self.frames == 2:
            self.timer.Clear()
            timer = celTimer(self.splash)
            timer.WakeUp(50, False)
            self.startLoading()
            
    def startLoading(self):
        print 'making garage'
        self.ents = []
        self.fconst = Menu.GetFontConstant()
        
        #Info needed to exit the garage
        self.returnname = ''
        self.returnbehaviour = ''
        #These two are pickled
        self.returnlobby = ''
        self.returngame = ''

        ioLoader.loadLibraryFolder('effects')
        ioLoader.loadWorldFolder('weapons', True)
        ioLoader.loadWorldFolder('vehicles', True)
        Engine.PrecacheDraw()

        gameworld = ioLoader.makeGameWorld('maps/garage')
        self.camera = celDefaultCamera(gameworld)
        self.camera.ModeName = 'freelook'
        self.camera.SetYawVelocity(0.2)
        
        bg = celAddBillboard(self.entity).Billboard
        bg.SetPosition(0, 0)
        bg.SetSize(80000, 307200)
        bg.SetMaterialName('window-frame')

        title = celAddBillboard(self.entity).Billboard
        title.SetTextFont('/outlaws/fonts/lcd2.ttf',self.fconst * 2.5)
        title.SetPosition(1000, 1000)
        title.SetTextFgColor(csColor(1, 1, 1))
        title.SetText('Garage')

        namelabel = celAddBillboard(self.entity).Billboard
        namelabel.SetTextFont('/outlaws/fonts/lcd2.ttf',self.fconst * 1.5)
        namelabel.SetPosition(5000, 25000)
        namelabel.SetTextFgColor(csColor(1, 1, 1))
        namelabel.SetText('Player Name')
        
        vehiclelabel = celAddBillboard(self.entity).Billboard
        vehiclelabel.SetTextFont('/outlaws/fonts/lcd2.ttf',self.fconst * 1.5)
        vehiclelabel.SetPosition(5000, 55000)
        vehiclelabel.SetTextFgColor(csColor(1, 1, 1))
        vehiclelabel.SetText('Vehicle')
        
        modellabel = celAddBillboard(self.entity).Billboard
        modellabel.SetTextFont('/outlaws/fonts/lcd2.ttf',self.fconst * 1.5)
        modellabel.SetPosition(5000, 130000)
        modellabel.SetTextFgColor(csColor(1, 1, 1))
        modellabel.SetText('Model Preset')

        self.vehiclescroller = ioScroller.ioScroller(self.entity, [00000, 65000], [80000, 50000])
        self.modelscroller = ioScroller.ioScroller(self.entity, [00000, 140000], [80000, 50000])
        
        self.buttons = Menu.ioMenu(self.entity)
        self.buttons.addElement('Continue','Continue_click', [280000, 0], [30000,10000], self.fconst,'half-black')

        self.inputs = Menu.ioMenu(self.entity)
        self.inputs.addElement('playername', 'input_click', [5000, 40000], [35000, 10000], self.fconst, 'button-bg', 'ioTextInput')
        
        for i, mount in enumerate(['Front1', 'Front2', 'Roof1', 'Roof2', 'Side1', 'Side2', 'Rear1', 'Rear2']):
            self.inputs.addElement(mount, 'input_click', [5000, 200000 + i * 10000], [70000, 7000], self.fconst, 'button-bg', 'ioDropDown')

        weaponsinfo = ioLoader.scanDir('weapons')
        #make a dictionary relating full names to codenames, and vice versa,so we can create entities
        self.codenames = {}
        #relate codenames to fullnames for loading
        self.fullnames = {}
        #relate codenames to paths for model scanning
        self.paths = {}
        for dict in weaponsinfo:
            name = dict['Name']
            codename = dict['Codename']
            self.codenames[name] = codename
            self.fullnames[codename] = name
            for dropdown in self.inputs.elements[1:]:
                pars = parblock(dict)
                dropdown.Behaviour.SendMessage('additem', None, pars)
        
        #Find the start position, to place the menu.
        if Engine.GetCameraPositions ().GetCount () > 0:
            self.startpos = Engine.GetCameraPositions ().Get (0).GetPosition()
        else:
            self.startpos = csVector3 (0)

        vehiclelist = ioLoader.scanDir('vehicles')

        self.selectedvehicle = None
        self.weapons = {}
        
        #Parse the vehicles
        for dict in vehiclelist:
            validdata = True
            n = 'Name'
            c = 'Codename'
            p = 'Path'
            #We know that the path will be there, since its added in the code
            for key in [n, c]:
                if not dict.has_key(key):
                    validdata = False
                    print 'Vehicle at path', dict['Path'], 'is missing config entry', key
                    print "Did you remember to include the 'info.cfg' file?"
            #Also test the entity template is valid.
            if dict.has_key(c):
                tplname = '%s-tpl' % dict[c]
                tpl = EntityTemplates[tplname]
                if not tpl:
                    validdata = False
                    print 'Entity template', tplname, "doesn't exist"
                
            if validdata:
                name = dict['Name']
                codename = dict['Codename']
                path = dict['Path']
                self.codenames[name] = codename
                self.fullnames[codename] = name
                self.paths[name] = path
                self.vehiclescroller.additem(name, 'vehiclescroller_select')
        
        self.loadSetup()
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'continue')
        pcinput.Bind('Left', 'camleft')
        pcinput.Bind('Right', 'camright')
        pcinput.Bind('Up', 'camup')
        pcinput.Bind('Down', 'camdown')

    def pccommandinput_camleft1(self, pc, args):
        self.camera.SetYawVelocity(0.6)

    def pccommandinput_camleft0(self, pc, args):
        self.camera.SetYawVelocity(0)


    def pccommandinput_camright1(self, pc, args):
        self.camera.SetYawVelocity(-0.6)

    def pccommandinput_camright0(self, pc, args):
        self.camera.SetYawVelocity(0)

    def pccommandinput_camup1(self, pc, args):
        self.camera.SetPitchVelocity(-0.6)

    def pccommandinput_camup0(self, pc, args):
        self.camera.SetPitchVelocity(0)

    def pccommandinput_camdown1(self, pc, args):
        self.camera.SetPitchVelocity(0.6)

    def pccommandinput_camdown0(self, pc, args):
        self.camera.SetPitchVelocity(0)

    def pccommandinput_camdown_(self, pc, args):
        pass

    #Load from the player's saved setup
    def loadSetup(self):
        vehicle = Config.GetStr('Outlaws.Player.Vehicle', self.codenames[self.vehiclescroller.names[0]])
        self.selectvehicle(self.fullnames[vehicle])

        for mount in ['Front1', 'Front2', 'Roof1', 'Roof2', 'Side1', 'Side2', 'Rear1', 'Rear2']:
            weapon = Config.GetStr('Outlaws.Player.' + mount, '')
            self.selectweapon(mount, weapon)

        #If this is the first time and no settings are saved, preselect the first model.
        if self.weapons == {}:
            if len(self.modelscroller.names) is 0:
                print 'Vehicle', self.fullnames[vehicle], 'has no models!'
            else:
                self.selectmodel(self.modelscroller.names[0])
            
        name = Config.GetStr('Outlaws.Player.Name', os.environ.get('USER'))
        celBillboard(self.inputs.elements[0]).Billboard.SetText(name)

    def input_click(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.inputs.activate(name)

    def input_click_item(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        ent = Entities[name]
        bb = celBillboard(ent).Billboard
        text = bb.GetText()
        self.selectweapon(name, self.codenames[text])

    def vehiclescroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.selectvehicle(name)
        if len(self.modelscroller.names) is 0:
                print 'Vehicle', name, 'has no models!'
        else:
            self.selectmodel(self.modelscroller.names[0])
        
    def modelscroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.selectmodel(name)
        
    def pccommandinput_continue1(self, pc, args):
        self.Continue_click(self.entity, celGenericParameterBlock(0))
        
    def pccommandinput_exit1(self, pc, args):
        pass
        
    def pccommandinput_exit_(self, pc, args):
        pass

    #Change the vehicle
    def selectvehicle(self, name):
        self.vehiclescroller.selectname(name)
        codename = self.codenames[name]
        path = self.paths[name]
        self.makevehicle(codename)
        self.modellist = ioLoader.scanModels(path)
        self.modelscroller.clear()
        for modelinfo in self.modellist:
            self.modelscroller.additem(modelinfo['Name'], 'modelscroller_select')

    #Update all weapons for a model
    def selectmodel(self, name):
        self.modelscroller.selectname(name)
        model = self.modellist[self.modelscroller.selectedindex]
        weapons = model['Weapons']
        for mount, weapon in weapons.items():
            self.selectweapon(mount, weapon)

    #Update the weapon dropdown and put it on the vehicle
    def selectweapon(self, mount, weapon):
        pars = parblock({'mount' : mount, 'weapon' : weapon})
        dropdown = Entities[mount]
        bb = celBillboard(dropdown).Billboard
        rcode = self.selectedvehicle.Behaviour.SendMessage('addweapon', None, pars)
        #print mount, rcode
        if rcode is 0:
            dropdown.Behaviour.SendMessage('setunlocked', None, celGenericParameterBlock(0))
            bb.SetTextFgColor(Menu.GetFontColor())
            self.weapons[mount] = weapon
            bb.SetText(self.fullnames[weapon])
        elif rcode is 1:
            dropdown.Behaviour.SendMessage('setlocked', None, celGenericParameterBlock(0))
            bb.SetText('Unavailable')
            bb.SetTextFgColor(csColor(0.2, 0.2, 0.2))
        elif rcode is 2:
            dropdown.Behaviour.SendMessage('setunlocked', None, celGenericParameterBlock(0))
            bb.SetTextFgColor(Menu.GetFontColor())
            bb.SetText('Bad Weapon Save')
            

    #Actually constructs the vehicle
    def makevehicle(self, codename):
        if self.selectedvehicle is not None:
            RemoveEntity(self.selectedvehicle)

        self.selectedvehicle = ioNetworkEntCl.makeEntity(codename, 'garagevehicle')
        if not self.selectedvehicle:
            print 'Failed to make vehicle with codename', codename
        else:
            vehiclemesh = celMesh(self.selectedvehicle)
            vehiclemesh.MoveMesh(Engine.GetSectors().Get(0), vehiclemesh.Mesh.GetMovable().GetPosition())
            self.camera.SetFollowEntity(self.selectedvehicle)
            vehiclemech = celGetMechanicsObject(self.selectedvehicle)
            vehiclemech.Body.SetPosition(self.startpos)
            #Put the brakes on so the car doesnt roll off.
            wheeled = celWheeled(self.selectedvehicle)
            if wheeled:
                wheeled.SetAutoReverse(False)
                wheeled.Brake(1.0)
                wheeled.Handbrake(True)
        
    #Return to caller, and save all the settings
    def Continue_click(self, pc, args):
        #Save the player setup
        self.inputs.deactivateAll()
        name = celBillboard(self.inputs.elements[0]).Billboard.GetText()
        Config.SetStr('Outlaws.Player.Name', name)
        Config.SetBool('Outlaws.Garage.Visited', True)
        Config.SetStr('Outlaws.Player.Vehicle', self.codenames[self.vehiclescroller.selectedname])
        for mount, weapon in self.weapons.items():
            Config.SetStr('Outlaws.Player.' + mount, weapon)
        Config.Save()

        returnname, returnbehaviour = ioDataBin.Get('lastmenu', True)
        #Recreate the entity which called the garage
        returnent = CreateEntity(returnname, self.blpython, returnbehaviour)
        if self.selectedvehicle:
            RemoveEntity(self.selectedvehicle)
        ioLoader.unloadGameWorld()
        RemoveEntity(self.entity)
        
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.buttons.clear()
        self.inputs.clear()
        self.vehiclescroller.destruct()
        self.modelscroller.destruct()    
        
