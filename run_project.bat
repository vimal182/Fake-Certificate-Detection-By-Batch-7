@echo off
cd /d %~dp0

call venv310\Scripts\activate

python home.py

pause