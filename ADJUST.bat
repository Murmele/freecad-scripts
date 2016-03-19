REM perform a sequence of commands for ALL files given as arguments to the script
for %%x in (%*) do (
REM perform a sequence of actions to a STEP file
freecad.exe %%x chain.FCMacro rx+ ry- az-
REM save the STEP file as a WRL (in the same directory) appropriately scaled for KiCAD
freecad.exe %%x step2wrl.FCMacro
)