"""
Various functions for transforming STEP files, and converting to WRL files
"""

import FreeCAD, FreeCADGui, Draft, ImportGui
import re
import math

import sys, os

        
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
            
#align the left-x side of the part to zero
def alignXLeft():
    moveAll(-getBounds(
    )['xMin'],0,0)
    
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
