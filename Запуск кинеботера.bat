@echo off
REM Перейти в каталог с приложением
cd /D d:\ExpoHelper

REM Проверка наличия виртуального окружения

REM Активация виртуального окружения
call .venv\Scripts\activate.bat

REM Запуск приложения
python Window.py

pause