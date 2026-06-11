@echo off
cd /d "%~dp0"

if exist "dist\AmpelClip.exe" (
    start "" "dist\AmpelClip.exe"
    exit /b 0
)

if exist "AmpelClip.exe" (
    start "" "AmpelClip.exe"
    exit /b 0
)

python "Ampel6.py"
