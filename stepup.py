import FreeCAD, FreeCADGui, Draft, ImportGui 
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui
import re
import math

import __builtin__

from collections import namedtuple

Mesh = namedtuple('Mesh', ['points', 'faces', 'color', 'transp'])

def getAllObjects():
    return FreeCAD.ActiveDocument.Objects
    
def getAllMeshes():
    meshes = []
    
    for obj in getAllObjects():
        meshes += objectToMesh(obj)
        
    return meshes

#Export a VRML model file
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