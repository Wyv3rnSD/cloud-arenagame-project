@echo off
setlocal
pushd "%~dp0"

python -m pip install -r requirements-build.txt
if errorlevel 1 (
    popd
    exit /b 1
)

python -m PyInstaller --clean --noconfirm --onefile --windowed --name CloudArena --paths client --add-data "server\server.py;server" launcher.py
if errorlevel 1 (
    popd
    exit /b 1
)

echo.
echo Build complete: %~dp0dist\CloudArena.exe
popd
endlocal
