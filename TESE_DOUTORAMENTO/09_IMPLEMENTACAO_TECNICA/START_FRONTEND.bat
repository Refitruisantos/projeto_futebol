@echo off
echo ========================================
echo Starting Football Analytics Frontend
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Download the LTS version and restart your terminal.
    echo.
    pause
    exit /b 1
)

echo Node.js found!
node --version
echo npm version:
npm --version
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    echo This will take a few minutes on first run.
    echo.
    call npm install
    echo.
)

echo Starting React development server...
echo Frontend will be available at: http://localhost:5173
echo.
call npm run dev
