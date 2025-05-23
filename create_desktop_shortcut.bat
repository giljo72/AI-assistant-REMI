@echo off
echo Creating desktop shortcut for AI Assistant...

:: Create shortcut on desktop
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Start AI Assistant.lnk'); $Shortcut.TargetPath = 'F:\assistant\startai.bat'; $Shortcut.WorkingDirectory = 'F:\assistant'; $Shortcut.IconLocation = 'F:\assistant\startai.bat'; $Shortcut.Description = 'Start AI Assistant with NeMo'; $Shortcut.Save()"

echo Desktop shortcut created: "Start AI Assistant.lnk"
echo You can now double-click the desktop icon to start the AI Assistant!
pause