from pycel import *
import os

#The glue module which abstracts the widgets into a menu. Allows one widget to have focus


def GetFontConstant():
    return 1.0 + float(Graphics2D.GetHeight()) / 100.0

def GetFontColor():
    return csColor(0.9, 0.9, 0.9)

class ioMenu:
    def __init__(self, owner):
        self.elements = []
        self.blpython = BehaviourLayers['blpython']
        self.owner = owner
        self.active = None
        self.font = '/outlaws/fonts/lcd2.ttf'
    
    #A generic menu element. sends message to menu when clicked if given one
    def addElement(self, name, message, position, sizes, fsize, material, behaviour = 'ioButton'):
        elementEntity = CreateEntity(name, self.blpython, None)
        pcbillboard = celBillboard(elementEntity)
        pcbillboard.materialnamefast = material
        pcbillboard.width = sizes[0]
        pcbillboard.height = sizes[1]
        pcbillboard.x = position[0]
        pcbillboard.y = position[1]
        pcbillboard.text_offset = csVector2(1500, 1500)
        pcbillboard.text_fg_color = GetFontColor()
        pcbillboard.text_font_size = fsize
        pcbillboard.text_font = self.font
        pcbillboard.text = name
        params=parblock({'message' : message, 'owner': self.owner})
        if message != '':
            elementEntity.CreateBehaviour(self.blpython, behaviour)
            pcbillboard.clickable = True
            elementEntity.Behaviour.SendMessage('setparameters', None, params)
        self.elements.append(elementEntity)
        return elementEntity

    def align(self, position, spacing):
        for i, element in enumerate(self.elements):
                bb = celBillboard(element).Billboard
                bb.SetPosition(position[0] + (spacing[0]*i),position[1]+(spacing[1]*i))
    
    def clear(self):
        for i in xrange(len(self.elements)):
            element = self.elements.pop(0)
            element.PropertyClassList.RemoveAll()
            RemoveEntity(element)
    
    def updateSelect(self, selected):
        index = 0
        for i, element in enumerate(self.elements):
            if element.Name == selected:
                index = i
            bb = celBillboard(element).Billboard
            bb.SetMaterialName('button-bg')
        
        bb = celBillboard(self.elements[index]).Billboard
        bb.SetMaterialName('button-bg')
        return index
            
    def menuFromList(self, items, message):
        for item in items:
            name = item['Name']
            if item.has_key('Preview') and item.has_key('Path'):
                preview = item['Preview']
                path = item['Path']
                print path
                Vfs.ChDir('/outlaws/ioData/' + path)
                Loader.LoadTexture(name + preview,  preview, CS_TEXTURE_2D)
            self.addElement(name, message, [0, 0], [90000, 27000], 18, 'button-bg')
            
    def remove(self, index):
        element = self.elements.pop(index)
        RemoveEntity(element)
            
    def activate(self, name):
        self.active = None
        for element in self.elements:
            if element.Name == name:
                if element.Behaviour:
                    self.active = element
                    element.Behaviour.SendMessage('setactive', None, celGenericParameterBlock(0))
            else:
                if element.Behaviour:
                    element.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))

    def deactivateAll(self):
        self.active = None
        for element in self.elements:
            if element.Behaviour:
                element.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
