@echo off
chcp 65001 >nul
title PC Checker - Build Tool
color 0B

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║      PC Status Checker - Build to .EXE      ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Please install Python 3.8+
    echo  Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [1/4] Installing dependencies...
pip install psutil wmi pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo  [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo  [2/4] Cleaning old build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

echo  [3/4] Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "PC_Status_Checker" ^
    --icon NONE ^
    --add-data "." ^
    --hidden-import psutil ^
    --hidden-import wmi ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import winreg ^
    --hidden-import socket ^
    --hidden-import threading ^
    --hidden-import platform ^
    --hidden-import datetime ^
    --hidden-import subprocess ^
    --hidden-import json ^
    --hidden-import ctypes ^
    --collect-all psutil ^
    --collect-all wmi ^
    --noconfirm ^
    pc_checker.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed!
    pause
    exit /b 1
)

echo  [4/4] Done!
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   Output: dist\PC_Status_Checker.exe        ║
echo  ║   Size  : check dist\ folder                ║
echo  ║                                              ║
echo  ║   Just copy the .exe to any Windows PC      ║
echo  ║   and double-click to run! No Python needed ║
echo  ╚══════════════════════════════════════════════╝
echo.

explorer dist
pause
