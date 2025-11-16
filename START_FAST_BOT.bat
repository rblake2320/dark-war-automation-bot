@echo off
echo ===============================================
echo     DARK WAR SURVIVAL FAST BOT LAUNCHER
echo ===============================================
echo.
echo Choose your speed:
echo 1. ULTRA FAST (recommended)
echo 2. SPEED DEMON (maximum speed)
echo 3. Normal Bot (slower but stable)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo Starting Ultra Fast Bot...
    python ultra_fast_bot.py
) else if "%choice%"=="2" (
    echo Starting Speed Demon...
    python speed_demon_bot.py
) else (
    echo Starting Normal Bot...
    python main.py
)

pause