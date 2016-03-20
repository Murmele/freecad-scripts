"""
Various functions for transforming STEP files, and converting to WRL files
"""

import FreeCAD, FreeCADGui, Draft, ImportGui

import sys, os

import re
import math

def getTempStepFile():
    step = os.path.split(getStepFile())
    
    return os.path.join(step[0],"tmp_" + step[1])

#get the abs-path for the 3D file provided
def getStepFile():
    step = sys.argv[1]
    filePath = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(step):
        step = os.path.join(filePath,step)
    return step
    
#create a .wrl file path based on the provided 3D file
def getWRLFile():
    return ".".join(getStepFile().split(".")[:-1]) + ".wrl"

#return the bounding-box for a given object
def getBoundBox(obj):
    return obj.Shape.BoundBox
    
#from a file-name extract the pin and pitch information
def getPadInformation(filename):
    n,pitch = 0,0
    
    #look for a string of the format "02x1.25mm"
    s = "(\d*)x([\.\d]*)mm"
    
    res = re.search(s,filename)
    
    if res and len(res.groups()) == 2:
        n, pitch = res.groups()
        
        try:
            n = int(n)
            pitch = float(pitch)
        except:
            n = 0,
            pitch = 0
            
    if n==0 or pitch == 0:
        showError("Could not find valid pin/pitch information in",filename)
    return (n,pitch)
    
#assuming pins are centered at zero, calculate the distance required to move such that pin-1 is then at zero
def offsetPins(n, pitch):
    if n%2 == 0:
        #even pins
        return (math.floor(n/2) - 0.5) * pitch
    else:
        #odd pins
        return math.floor(n/2) * pitch
        
def padX():
    n,p = getPadInformation(getStepFile())
    d = offsetPins(n,p)
    
    moveAll(d,0,0)
    
def padY():
    n,p = getPadInformation(getStepFile())
    d = offsetPins(n,p)
    
    moveAll(0,d,0)
    
def padZ():
    n,p = getPadInformation(getStepFile())
    d = offsetPins(n,p)
    
    moveAll(0,0,d)
    
#add a new bounding-box to an ever-expanding bounding-box
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
        
#get the bounding box (of ALL components in the document)
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
    y = (b['yMin'] + b['yMax']) / 2
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
        
#grab all objects, and export to a STEP file
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
        
#grab all objects and save to a WRL file
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
                
#print an error message in the FreeCAD console
def showError(*args):
    FreeCAD.Console.PrintError("Error: " + " ".join(map(str,args)) + "\n")
    
#print a general message in the FreeCAD console
def showMessage(*args):
    FreeCAD.Console.PrintMessage(" ".join(map(str,args)) + "\n")
    
def rotate_x():
    rotateAll(90,(1,0,0))
    
def rotate_y():
    rotateAll(90,(0,1,0))
    
def rotate_z():
    rotateAll(90,(0,0,1))