"""
Various functions for transforming STEP files, and converting to WRL files
"""

import FreeCAD, FreeCADGui, Draft, ImportGui

import sys, os

FreeCADGui.ActiveDocument.ActiveView.setAxisCross(True)

def getTempStepFile():
    step = os.path.split(getStepFile())
    
    print(step)
    
    return os.path.join(step[0],"tmp_" + step[1])

def getStepFile():
    step = sys.argv[1]
    filePath = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(step):
        step = os.path.join(filePath,step)
    return step
    
def getWRLFile():
    return ".".join(getStepFile().split(".")[:-1]) + ".wrl"

def getBoundBox(obj):
    return obj.Shape.BoundBox
    
def addBounds(box, bounds=None):
    if not bounds:
        bounds = {}
        bounds['xMin'] = box.XMin
        bounds['yMin'] = box.YMin
        bounds['zMin'] = box.ZMin
        bounds['xMax'] = box.XMax
        bounds['yMax'] = box.YMax
        bounds['zMax'] = box.ZMax
    else:
        bounds['xMin'] = min(bounds['xMin'],box.XMin)
        bounds['xMax'] = max(bounds['xMax'],box.XMax)
        
        bounds['yMin'] = min(bounds['yMin'],box.YMin)
        bounds['yMax'] = max(bounds['yMax'],box.YMax)
        
        bounds['zMin'] = min(bounds['zMin'],box.ZMin)
        bounds['zMax'] = max(bounds['zMax'],box.ZMax)

    return bounds
        
#get the bounding box (of ALL components in a group)
def getBounds():

    objs = getAll()
    
    bounds = addBounds(getBoundBox(objs[0]))
    
    for obj in objs[1:]:
        bounds = addBounds(getBoundBox(obj),bounds)
        
    return bounds
            
#align the left-x side of the part to zero
def alignXLeft():
    moveAll(-getBounds()['xMin'],0,0)
    
def alignXRight():
    moveAll(-getBounds()['xMax'],0,0)
    
def alignXMiddle():
    b = getBounds()
    x = (b['xMin'] + b['xMax']) / 2
    moveAll(-x,0,0)
    
def alignYMiddle():
    b = getBounds()
    x = (b['yMin'] + b['yMax']) / 2
    moveAll(0,-y,0)
    
def alignZMiddle():
    b = getBounds()
    z = (b['zMin'] + b['zMax']) / 2
    moveAll(0,0,-z)
    
#align the TOP (Y) to the x axis
def alignYTop():
    moveAll(0,-getBounds()['yMax'],0)
    
def alignYBottom():
    moveAll(0,-getBounds()['yMin'],0)
    
def alignZTop():
    moveAll(0,0,-getBounds()['zMax'])
    
def alignZBottom():
    moveAll(0,0,-getBounds()['zMin'])
    
def moveAll(x,y,z):
    Draft.move(getAll(),FreeCAD.Vector(x,y,z))

#find and return all objects
def getAll():
    return FreeCAD.ActiveDocument.Objects
    
#scale ALL objects around center (down to inches for KiCAD)
def scaleAll(scaling):

    if type(scaling) in [int, float]:
        x = scaling
        y = scaling
        z = scaling
    else:
        x,y,z = scaling

    scale = FreeCAD.Vector(x,y,z)
    origin = FreeCAD.Vector(0,0,0)

    Draft.scale(getAll(), delta=scale, center=origin, legacy=True, copy=False)
        
def saveSTEP(filename):
    objs = getAll()

    ImportGui.export(objs,filename)
    
    del objs
    
#if the "tmp" arg is passed, save with a tmp_ prefix and DO NOT CLOSE!
def saveStepAndClose():
    if "tmp" in sys.argv:
        out = getTempStepFile()
        saveSTEP(out)
    else:
        out = getStepFile()
        saveSTEP(out)
        exit()
        
def saveWRL(filename):
    objs = []
    
    for obj in getAll():
        FreeCADGui.Selection.addSelection(obj)
        objs.append(obj)
        
    FreeCADGui.export(objs, filename)
    
    del objs
        
#rotate 90 degrees across a given axis
#centered around zero
def rotateAll(angle,axes):

    objs = getAll()

    origin = FreeCAD.Vector(0,0,0)
    x,y,z = axes
    axis = FreeCAD.Vector(axes)
    
    Draft.rotate(objs,
                angle,
                origin,
                axis=axis,
                copy=False)
                
def showError(*args):
    FreeCAD.Console.PrintError(" ".join(map(str,args)) + "\n")
    
def showMessage(*args):
    FreeCAD.Console.PrintMessage(" ".join(map(str,args)) + "\n")
                
def rotate_x():
    rotate((1,0,0))
    
def rotate_y():
    rotate((0,1,0))
    
def rotate_z():
    rotate((0,0,1))