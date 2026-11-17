@echo off
cd /d "%~dp0"
python -X utf8 tools\start_fuxa_zh.py
if errorlevel 1 pause
