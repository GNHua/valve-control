@echo off

:: navigate to root folder
cd %~dp0\..\..
:: assign root folder to a variable
set PROJECT_ROOT=%cd%
:: start program in the background
start pythonw %PROJECT_ROOT%\run.py