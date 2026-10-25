@echo off
chcp 65001 >nul
title PC Status & License Checker

:: Kiem tra neu khong co Python thi chay truc tiep tu dist\PC_Status_Checker.exe
python --version >nul 2>&1
if errorlevel 1 (
    if exist "dist\PC_Status_Checker.exe" (
        start "" "dist\PC_Status_Checker.exe"
        exit /b 0
    ) else (
        echo  [!] May tinh chua cai Python va chua co file dist\PC_Status_Checker.exe
        echo  [!] Vui long tai Python tai https://www.python.org hoac chay PC_Status_Checker.exe
        pause
        exit /b 1
    )
)

:: Tu dong cai dat thu vien neu thieu
python -c "import psutil, wmi" >nul 2>&1 || (
    echo  [*] Dang cai dat thu vien can thiet (psutil, wmi)...
    python -m pip install psutil wmi --quiet
)

:: Chay ung dung
start "" pythonw pc_checker.py
