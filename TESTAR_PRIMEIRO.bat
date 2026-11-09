@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel% equ 0 (set PY=py -3) else (set PY=python)
%PY% -m venv .venv
if errorlevel 1 (echo ERRO: Python 3.10 ou superior necessario.&pause&exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 (echo ERRO ao instalar as bibliotecas.&pause&exit /b 1)
python -m unittest discover -s testes -v
if errorlevel 1 (echo ERRO NOS TESTES.&pause&exit /b 1)
python executar.py --modo piloto --repeticoes 3 --geracoes 30 --populacao 30
pause
