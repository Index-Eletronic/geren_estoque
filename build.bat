@echo off
title Build - Sistema de Estoque

cd /d "%~dp0"

set APP_NAME=SistemaEstoque
set ICON_FILE=%~dp0icon.ico

echo ========================================
echo   GERANDO EXECUTAVEL DO SISTEMA
echo ========================================
echo.

py -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    py -m pip install pyinstaller
)

py -m pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo openpyxl nao encontrado. Instalando...
    py -m pip install openpyxl
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %APP_NAME%.spec del /f /q %APP_NAME%.spec
if exist main.spec del /f /q main.spec

if exist "%ICON_FILE%" (
    echo Icone encontrado: %ICON_FILE%
    py -m PyInstaller --clean --noconfirm --windowed --onedir --name "%APP_NAME%" --icon "%ICON_FILE%" --add-data "estoque.db;." main.py
) else (
    echo Icone nao encontrado. Gerando sem icone.
    py -m PyInstaller --clean --noconfirm --windowed --onedir --name "%APP_NAME%" --add-data "estoque.db;." main.py
)

echo.
echo ========================================
echo   PROCESSO FINALIZADO
echo ========================================
echo.

if exist dist\%APP_NAME%\%APP_NAME%.exe (
    echo Executavel gerado em:
    echo dist\%APP_NAME%\%APP_NAME%.exe
) else (
    echo O executavel nao foi gerado.
)

echo.
pause