@echo off
REM Start GitCode Proxy Server for CANN Recipes Blog

echo Starting GitCode Proxy Server...
echo.

cd proxy

REM Check if Node.js is available
where node >nul 2>nul
if %errorlevel% equ 0 (
    echo Using Node.js proxy...
    node proxy.js
) else (
    echo Node.js not found. Using Python proxy...
    python proxy_server.py
)

pause