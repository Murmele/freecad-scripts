import FreeCAD, FreeCADGui, Draft, ImportGui 
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui
import re
import math

import os,sys

import __builtin__

from collections import namedtuple

Mesh = namedtuple('Mesh', ['points', 'faces', 'color', 'transp'])

#return all objects in Active Document
def getAllObjects():
    return FreeCAD.ActiveDocument.Objects
    
#return all selected objects in Active Document
def getSelectedObjects():
    return FreeCADGui.Selection.getSelectionEx()
    
#return combined meshes of all objects in Active Document
def getAllMeshes():
    meshes = []
    
    for obj in getAllObjects():
        meshes += objectToMesh(obj)
        
    return meshes

#Export a VRML model file with the selected meshes
def exportVRMLMeshes(meshes, filepath):
    """Export given list of Mesh objects to a VRML file.

    `Mesh` structure is defined at root."""
    
    with __builtin__.open(filepath, 'w') as f:
        # write the standard VRML header
        f.write("#VRML V2.0 utf8\n\n")
        for mesh in meshes:
            f.write("Shape { geometry IndexedFaceSet \n{ coordIndex [")
            # write coordinate indexes for each face
            f.write(','.join("%d,%d,%d,-1" % f for f in mesh.faces))
            f.write("]\n") # closes coordIndex
            f.write("coord Coordinate { point [")
            # write coordinate points for each vertex
            #f.write(','.join('%.3f %.3f %.3f' % (p.x, p.y, p.z) for p in mesh.points))
            f.write(','.join('%.3f %.3f %.3f' % (p.x, p.y, p.z) for p in mesh.points))
            f.write("]\n}") # closes Coordinate
            #shape_col=(1.0, 0.0, 0.0)#, 0.0)
            f.write("}\n") # closes points
            #say(mesh.color)
            shape_col=mesh.color[:-1] #remove last item
            #say(shape_col)
            shape_transparency=mesh.transp
            f.write("appearance Appearance{material Material{diffuseColor %f %f %f\n" % shape_col)
            f.write("transparency %f}}" % shape_transparency)
            f.write("}\n") # closes Shape
        say(filepath,"written")
        
#return a 'view' of the object, with attributes such as color/transparency
def getObjectView(object):
    return FreeCADGui.ActiveDocument.getObject(object.Name)
    
#convert an object to a list of mesh    
def objectToMesh(object, scale=None):
    view = getObjectView(object)
    shape = object.Shape
    
    deviation = 0.03
    
    color = view.DiffuseColor
    transparency = view.Transparency
    
    #list of meshes
    meshes = []
    
    #if there are fewer colors than faces, apply one color to all faces
    if len(color) < len(shape.Faces):
        applyDiffuse = False
    else:
        applyDiffuse = True
    
    for i,face in enumerate(shape.Faces):
        
        if applyDiffuse: #apply individual face colors
            col = color[i]
        else: #apply one color to all faces
            col = color[0]
            
        meshes.append(faceToMesh(face,col,transparency,deviation,scale))
    
    return meshes
    
#Convert a face to a mesh
def faceToMesh(face, color, transp, mesh_deviation, scale=None):
    #mesh_deviation=0.1 #the smaller the best quality, 1 coarse
    #say(mesh_deviation+'\n')
    mesh_data = face.tessellate(mesh_deviation)
    points = mesh_data[0]
    
    if scale:
        points = map(lambda p: p*scale, points)
        
    newMesh = Mesh(points = points,
                faces = mesh_data[1],
                color = color,
                transp=transp)
    
    return newMesh
    
#display a console message
def say(*arg):
    FreeCAD.Console.PrintMessage(" ".join(map(str,arg)) + "\n")

#display a warning message
def sayw(*arg):
    FreeCAD.Console.PrintWarning(" ".join(map(str,arg)) + "\n")
    
#display an error message
def sayerr(*arg):
    FreeCAD.Console.PrintError(" ".join(map(str,arg)) + "\n")

#clear the console
def clear_console():
    #clearing previous messages
    mw=FreeCADGui.getMainWindow()
    c=mw.findChild(QtGui.QPlainTextEdit, "Python console")
    c.clear()
    r=mw.findChild(QtGui.QTextEdit, "Report view")
    r.clear()
    
#work out where the KiCAD 3D directory is
def getKicad3DModDir():
    
    KISYS3DMOD = os.getenv("KISYS3DMOD",None)
    
    if KISYS3DMOD:
        return KISYS3DMOD
        
    guesses = [
    #windows paths
    r'C:\kicad\share\kicad\modules\packages3d',
    r'C:\kicad\share\packages3d',
    r'C:\program files\kicad\share\modules\packages3d',
    r'C:\program files\kicad\share\packages3d',
    #nix paths
    ]
    
    for guess in guesses:
        if os.path.isdir(guess):
            return guess
            
    return ''
    
#find a STEP file for a given wrl file
def getKicadStepFile(dir_3d, wrl_name):
    
    #get rid of bad path separators
    wrl_name = wrl_name.replace("/",os.path.sep)
    wrl_name = wrl_name.replace("\\",os.path.sep)
    
    steps = [
    ".step",
    ".STEP",
    ".stp",
    ".STP"
    ]
    
    if wrl_name.endswith(".wrl"):
        for step in steps:
            step_name = wrl_name.replace(".wrl",step)
            
            step_file = os.path.join(dir_3d, step_name)
            
            if os.path.isfile(step_file):
                return step_file
                
    return None
    
#rotate 90 degrees across a given axis
#centered around zero
def rotateAll(angle,axes):

    objs = getAllObjects()

    origin = FreeCAD.Vector(0,0,0)
    x,y,z = axes
    axis = FreeCAD.Vector(axes)
    
    Draft.rotate(objs,
                angle,
                origin,
                axis=axis,
                copy=False)
                
                
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

    Draft.scale(getAllObjects(), delta=scale, center=origin, legacy=True, copy=False)
         
#move all objects 
def moveAll(x,y,z):
    Draft.move(getAllObjects(),FreeCAD.Vector(x,y,z))
    
#get the consolidated bounding box for a group of objects
def getBounds(objs):

    box = objs[0].Shape.BoundBox
    
    for obj in objs[1:]:
        b = obj.Shape.BoundBox
        
        #x axis comparison
        box.XMin = min(box.XMin,b.XMin)
        box.XMax = max(box.XMax,b.XMax)
        
        #y axis comparison
        box.YMin = min(box.YMin,b.YMin)
        box.YMax = max(box.YMax,b.YMax)
        
        #z axis comparison
        box.ZMin = min(box.ZMin,b.ZMin)
        box.ZMax = max(box.ZMax,b.ZMax)
    
    return box
    
#calculate the required pin-offset based on filename
def getPinOffset(filename):
    
    res = re.search("(\d*)x([\.\d]*)mm",filename)
    
    if res and len(res.group()) == 2:
        n, pitch = res.groups()
        
        try:
            n = int(n)
            pitch = float(pitch)
            
            if n%2 == 0: #even pins
                return (math.floor(n/2) - 0.5) * pitch
            else: #odd pins
                return math.floor(n/2) * pitch
            
        except:
            pass
            
    return 0
    
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
    
#get a path to a temp copy of the provided step file
def getTempStepFile():
    step = os.path.split(getStepFile())
    
    return os.path.join(step[0],"tmp_" + step[1])
    