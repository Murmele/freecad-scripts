# freecad-scripts
FreeCAD scripts for converting STEP files to KiCAD-compatible WRL files. These scripts allow STEP files to be quickly adjusted to match KiCAD rotation/offset parameters, scaled to inferial inches, and converted to KiCAD-friendly .wrl files. 

##Files
- freecad.py - a number of functions for adjusting models in freecad programatically
- step2wrl.FCMacro - a FreeCad Macro file (really just a .py file in disguise) that takes an input STEP file, scales it by 1/2.54 (inches, blergh) and saves as a .wrl file for easy KiCAD consumption
- STEP2WRL.bat - a windows batch script that allows multiple STEP files to be processed by the step2wrl macro
- chain.FCMacro - A FreeCad macro file that accepts a sequence of short-hand commands (e.g. rotation, alignment, movement), applies them in sequence to the provided STEP file, and then re-saves the STEP file in the same location.
- ADJUST.bat - a windows batch script that allows multiple STEP files to be processed using the same sequence of commands 

###Requirements
- Install [FreeCAD](http://www.freecadweb.org/)
- Have fun

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

**Scaling** - *Scale the part by the given amount (around the origin)*

s=f (scale the part by scaling-factor 'f')

**Pin Offset** - *Automagically offset the position of the part along a given axis such that pin-1 is at zero on that axis*

p=[x|y|z] - Specify that we want to auto-align pin-1 along a given axis

This option can save a *lot* of time either adjusting the 3D model so that pin-1 (for THT parts) is at the origin, or adjusting the offset of the WRL file in KiCAD so that it matches the footprint. This is the most complicated command but provides powerful functionality if used correctly. The file-name of the input STEP file needs to include pin-count and pitch information, in the format '*pins*x*pitch*mm' (for example: *JST_PUD_S34B-PUDSS-1_2x17x2.00mm_Angled.STEP*) will be evaluated as 17 pins, 2.00mm pitch. 

*Note: Yes, this part actually has 34 pins, but it's split into two rows, and it is the pins-per-row that we are really interested in.*

For example, if the pins are distributed along the x-axis, we can use the command 'p=x'. The script will first center the part on the x-axis, and then offset it by the requisite amount such that pin-1 is at the origin.

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

##Example##

Let's try out an example.

We've downloaded a manufacturer STEP file that is aligned differently to how we would like it aligned to match our KiCAD footprint. Sometimes, manufacturers supply models which don't match KiCAD's xyz alignment. We can fix that.

In this example, we have a STEP file for the JST S34B-PUDSS-1 connector. We've renamed it to "JST_PUD_S34B-PUDSS-1_2x17x2.00mm_Angled.STEP" to match the footprint name. Note that the rows-pins-pitch information is embedded in the filename.

Let's open it up in FreeCAD and see how we need to manipulate it.

![alt tag](example/pud_before.png?raw=True "Before")

So the axes are incorrect - z-axis (blue) should be pointing "up" (where the green y-axis is currently). So we need to rotate the part 90 degrees around the x-axis. Also, pin-1 is not at the origin as per THT footprint requirements. We can take care of the x-alignment of pin-1 automatically by giving the 'p=x' command. We can also offset the y-axis appropriately. We determine (by measuring the part in FreeCAD) that the part needs to be moved -5.75mm on the y-axis.

Three operations are required. They can easily be chained together using the chain macro, as follows:

freecad.exe KISYS3DMOD/Connectors_JST.3dshapes/JST_PUD_S34B-PUDSS-1_2x17x2.00mm_Angled.STEP chain.FCMacro rx+ my=-5.75 p=x tmp

(we use the 'tmp' command to prevent overwriting the original STEP file, so we can confirm that the commands are correct).

![alt tag](example/pud_after.png?raw=True "After")

Success! The axes are aligned correctly, and pin-1 is bang on the origin. How does it look in KiCAD?

Run the chain command again, without the 'tmp' argument to make the changes stick.

Then, run the step2wrl macro to make a KiCAD-compatible wrl file

freecad.exe KISYS3DMOD/Connectors_JST.3dshapes/JST_PUD_S34B-PUDSS-1_2x17x2.00mm_Angled.STEP step2wrl.FCMacro

Now refresh the model in KiCAD

![alt tag](example/pud_kicad.png?raw=True "KiCAD")

Perfect! Without any adjustments to Scale/Offset/Rotation in KiCAD.

Once we have figured out the sequence for adjusting *one* component, we can automate the rest of the components in the series. Say we download *all* the SxxB-PUDSS-1 3D models, we can simply batch convert them all at once, by making a simple adjustment to the provided batch file (or a shell script for our *nix friends). This way you can drag-and-drop all your files onto the script, and the correct changes will be made to *all* the STEP files.

You can even chain the step2wrl.FCMacro command into the batch file so that both processes are executed in series.

##Build Your Own##
Play around with a sequence of commands or check out the options available in freecad.py


