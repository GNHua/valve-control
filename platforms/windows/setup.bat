@echo off

:: navigate to root folder
cd %~dp0\..\..
:: assign root folder to a variable
set PROJECT_ROOT=%cd%
:: install python dependencies
pip install -r %wikidir%\app\requirements.txt