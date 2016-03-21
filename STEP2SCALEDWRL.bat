cd %~p0
for %%x in (%*) do (
freecad.exe %%x step2wrl.FCMacro 
)