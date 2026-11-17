@echo off
cd /d "%~dp0"
python -X utf8 tools\install_fuxa.py
if errorlevel 1 pause
