# freecad-scripts
FreeCAD scripts primarily for converting STEP files to KiCAD-compatible WRL files

##Files
- freecad.py - a number of functions for adjusting models in freecad programatically
- step2wrl.FCMacro - a FreeCad Macro file (really just a .py file in disguise) that takes an input STEP file, scales it by 1/2.54 (inches, blergh) and saves as a .wrl file for easy KiCAD consumption
- STEP2WRL.bat - a windows batch script that allows multiple STEP files to be processed by the step2wrl macro
- chain.FCMacro - A FreeCad macro file that accepts a sequence of short-hand commands (e.g. rotation, alignment, movement), applies them in sequence to the provided STEP file, and then re-saves the STEP file in the same location.
- ADJUST.bat - a windows batch script that allows multiple STEP files to be processed using the same sequence of commands 

##Adjustment Chain
The *chain* macro allows the user to provide a 3D model to FreeCAD, and then sequence of commands to perform (in order) to that model. This is a powerful (and quick!) way of converting a 3D model into the correct XYZ orientation, and planar alignment for inclusion in KiCAD as a .wrl file.
This way, you can download *free* STEP files from a number of sources, and quickly orient them to your footprint.
Additionally, once you have worked out the sequence of commands required to orient the 3D model, you can use the ADJUST.bat script to apply that sequence to a large number of STEP files.

###Usage
To use the *chain* macro, you launch freecad from the command-line, with the STEP file as the first argument, chain.FCMacro as the second, and any transformation commands follow.

freecad.exe path/to/model.STEP chain.FCMacro [cmd1] [cmd2] ... [cmdn] [tmp]

###Commands
The following commands are available for the *chain* macro

**tmp** - Including 'tmp' as an argument will not overwrite the original file, instead the file will be saved with the prefix *tmp_*. This allows experimentation with the adjustment chain without damaging the STEP file.

**Rotational** - *rotate the component 90degrees around the origin (0,0,0)*

rx+ (rotate +90 degrees around X axis)

rx- (rotate -90 degrees around X axis)

ry+ (rotate +90 degrees around Y axis)

ry- (rotate -90 degrees around Y axis)


rz+ (rotate +90 degrees around Z axis)

rz- (rotate -90 degrees around Z axis)



**Alignment** - *align one of the sides of the part with the origin*

ax+ (align right side of part with yz plane)

ax- (align left side of part with yz plane)

ax  (align center of part with yz plane)

ay+ (align top side of part with xz plane)

ay- (align bottom side of part with xz plane)

ay  (align center of part with xz plane)

az+ (align top side of part with xy plane)

az- (align bottom side of part with xy plane)

az  (align center of part with xy plane)



**Movement** - *move the part along a given axis*

mx=d (move part along x-axis by d)

my=d (move part along y-axis by d)

mz=d (move part along z-axis by d)
