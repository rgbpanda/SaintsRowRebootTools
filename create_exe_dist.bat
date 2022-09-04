@echo off
set /p "ver=Enter Version: "
echo SRRebootTools%ver%
mkdir ..\SRRebootTools%ver%
xcopy /e . ..\SRRebootTools%ver%
cd ..\SRRebootTools%ver%
pyinstaller src/gui.py
rd /s /q build
robocopy /move /e dist\gui .
rd /s /q dist
move gui.exe SRRebootTools%ver%.exe
rd /s /q .vscode
powershell Compress-Archive . SRRebootTools%ver%.zip
move SRRebootTools%ver%.zip ..\
cd ..
rd /s /q SRRebootTools%ver%