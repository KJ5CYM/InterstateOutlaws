from pycel import *
import cPickle

import ioNetHelper

     
#Behaviour for a networked object
class ioNetworkEntBase:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.mesh = celMesh(self.entity)
        self.mech = celMechanicsObject(self.entity)
        self.body = self.mech.Body
        self.inputs = []
        self.registered = False
        #Only send position every 4 seconds, but vel every second
        self.ticks = 0
        self.front = csVector3(0, 0, -1)
        self.codename = ''
        self.net = ioNetHelper.ioNetHelper()

    ##Interpolate our rotation for 150ms
    def pctimer_wakeupframe(self, pc, args):
        pass
            
    def pctimer_wakeup(self, pc, args):
        pass

    #Get position from server
    def r_p(self, pc, args):
        addr, data = self.net.getNetData(args)
        pos = csVector3(*data[0:3])
        lvel = csVector3(*data[3:6])
        diff = pos - self.body.GetPosition()
        distance = diff.Norm()
        correction = csVector3(0)
        #If difference is too great, reset position
        if distance > 5.0:
            print 'setting position'
            self.body.SetPosition(pos)
            self.unstuck(False)
        #Otherwise do a little correction
        elif distance > 0.1:
            correction = diff * 2.0
        self.body.SetLinearVelocity(lvel + correction)
        
    #Get quaternion from server. Work out some stuff in order to add a torque to our body to correct it.
    #This function took half a year of tweaking to make it sorta work.
    def r_q(self, pc, args):
        addr, data = self.net.getNetData(args)
        v = csVector3(*data[0:3])
        w = data[3]
        avel = csVector3(*data[4:7])
        srvquat = csQuaternion(v, w)
        clquat = csQuaternion()
        clquat.SetMatrix(self.body.GetTransform().GetT2O())
        clquat.Conjugate()
        srvquat.Conjugate()
        correction = csVector3(0)
        #Work out the differences
        error = (srvquat - clquat).Norm()
        #If it goes more than 90 degrees the client risks aligning back to front
        if error > 0.7:
            ctrans = csOrthoTransform(srvquat.GetMatrix(), csVector3(self.body.GetPosition()))
            self.body.SetTransform(ctrans)
        #Elif error is noticeable, correct it with a torque
        elif error > 0.00025:
            #Rotate the front vector by both quaternions
            f1 = srvquat.Rotate(self.front)
            f2 = clquat.Rotate(self.front)
            #Find the cross product and dot product of the rotated vectors, to get the torque angles and magnitude
            cross = csVector3(0)
            cross.Cross(f1, f2)
            dot = f1 * f2
            correction = cross * dot
        if self.isupsidedown():
            correction = -correction
        #There seem to be errors in x and y correction, so we'll make y dominant
        correction = csVector3(correction.x * 2.0, correction.y * 5.0, correction.z * 2.0)
        self.body.SetAngularVelocity(avel + correction)

    def setcodename(self, pc, args):
       idCodename = getid('cel.parameter.codename')
       self.codename = args[idCodename]
       
    def setregistered(self, pc, args):
        self.registered = args[getid('cel.parameter.registered')]

    def destruct(self, pc, args):
        pass
    
    def sendinput(self, inp):
        pass
        
    def isupsidedown(self):
        if self.body.GetTransform().This2Other(csVector3(0,1,0)).y < self.body.GetPosition().y:
            return True
        else:
            return False    
        
    #Get the quaternion that defines rotation
    def getQuat(self):
        qt = csQuaternion()
        qt.SetMatrix(self.body.GetTransform().GetT2O())
        av = self.body.GetAngularVelocity()
        info = [qt.v.x, qt.v.y, qt.v.z, qt.w, av.x, av.y, av.z]
        #We round to reduce bandwidth
        sendinfo = [round(x, 3) for x in info]
        return sendinfo

    #Get our position, and linear velocity
    def getPos(self):
        pos = self.body.GetPosition()
        lv = self.body.GetLinearVelocity()
        info = [pos.x, pos.y, pos.z, lv.x, lv.y, lv.z]
        #We round to reduce bandwidth
        sendinfo = [round(x, 3) for x in info]
        return sendinfo