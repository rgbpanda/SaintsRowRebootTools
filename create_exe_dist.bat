@echo off
set /p "ver=Enter Version: "
echo SRRebootTools%ver%
mkdir ..\SRRebootTools%ver%
xcopy /e . ..\SRRebootTools%ver%
cd ..\SRRebootTools%ver%
pyinstaller src/app/gui.py
python3 -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
python3 -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
rd /s /q build
robocopy /move /e dist\gui .
rd /s /q dist
robocopy /e src\dist dist
move gui.exe SRRebootTools%ver%.exe
rd /s /q .vscode
powershell Compress-Archive . SRRebootTools%ver%.zip
move SRRebootTools%ver%.zip ..\
cd ..
rd /s /q SRRebootTools%ver%