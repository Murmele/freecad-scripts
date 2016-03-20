cd %~p0
for %%x in (%*) do (
start "" freecad.exe %%x step2wrl.FCMacro 
)