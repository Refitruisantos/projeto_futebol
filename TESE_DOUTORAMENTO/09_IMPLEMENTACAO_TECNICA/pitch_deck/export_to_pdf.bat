@echo off
echo Exporting pitch deck to PDF...

REM Check if Chrome is installed
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% (
    set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

REM Export to PDF
%CHROME% --headless --disable-gpu --print-to-pdf="pitch_deck.pdf" "%~dp0index.html"

echo.
echo PDF exported to: %~dp0pitch_deck.pdf
pause
