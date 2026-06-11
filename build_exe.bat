@echo off
setlocal
cd /d "%~dp0"

set "BUILD_ROOT=C:\_Local_DEV\codex_build\ampelclip"
set "PYTHONIOENCODING=utf-8"

python -m PyInstaller AmpelTool_V6.spec ^
  --distpath "%BUILD_ROOT%\dist" ^
  --workpath "%BUILD_ROOT%\work" ^
  --clean ^
  -y

if errorlevel 1 exit /b %errorlevel%

if not exist "dist" mkdir "dist"
copy /Y "%BUILD_ROOT%\dist\AmpelClip.exe" "dist\AmpelClip.exe"
copy /Y "%BUILD_ROOT%\dist\AmpelClip.exe" "AmpelClip.exe"

endlocal
