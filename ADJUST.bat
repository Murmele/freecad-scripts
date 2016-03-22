cd %~p0
REM perform a sequence of commands for ALL files given as arguments to the script
for %%x in (%*) do (
REM perform a sequence of actions to a STEP file
freecad.exe %%x chain.FCMacro rz+ rz+ az- ax ay tmp
)