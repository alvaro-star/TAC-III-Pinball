@echo off
setlocal
cd /d "%~dp0"
title Pinball TAC III - Instalacao e jogo

echo.
echo ===========================================
echo  PINBALL TAC III - PYTHON / PYGAME / OPENGL
echo ===========================================
echo.

if exist ".venv\Scripts\python.exe" goto dependencies

where py >nul 2>nul
if not errorlevel 1 (
    echo Criando ambiente virtual Python...
    py -3.12 -m venv .venv >nul 2>nul
    if exist ".venv\Scripts\python.exe" goto dependencies
    py -3.11 -m venv .venv >nul 2>nul
    if exist ".venv\Scripts\python.exe" goto dependencies
    py -3 -m venv .venv
    goto dependencies
)
where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado.
    echo Instale Python 3.11 ou 3.12 com a opcao "Add Python to PATH".
    pause
    exit /b 1
)
echo Criando ambiente virtual Python...
python -m venv .venv

:dependencies
if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Nao foi possivel criar o ambiente virtual.
    pause
    exit /b 1
)
echo Instalando/verificando pygame e PyOpenGL...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar dependencias. Verifique internet e Python.
    pause
    exit /b 1
)
echo.
echo Iniciando Pinball TAC III...
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo O jogo encerrou com erro. Confira a mensagem acima.
    pause
    exit /b 1
)
endlocal
