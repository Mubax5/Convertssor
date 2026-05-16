@echo off
setlocal

cd /d "%~dp0"
title Asset Converter

echo ========================================
echo Asset Converter - Auto Install and Run
echo ========================================
echo.

if not exist "App.py" (
    echo ERROR: App.py tidak ditemukan di folder ini.
    echo Pastikan run.bat berada satu folder dengan App.py
    echo.
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan.
    echo Install Python dulu, lalu centang "Add python.exe to PATH" saat install.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Gagal membuat virtual environment.
        echo.
        pause
        exit /b 1
    )
)

echo Mengaktifkan virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Gagal mengaktifkan virtual environment.
    echo.
    pause
    exit /b 1
)

echo Menginstall / update dependency...
python -m pip install --upgrade pip
python -m pip install customtkinter pillow pillow-avif-plugin
if errorlevel 1 (
    echo ERROR: Gagal install dependency.
    echo Coba cek koneksi internet lalu jalankan ulang file ini.
    echo.
    pause
    exit /b 1
)

echo.
echo Mengecek FFmpeg untuk fitur video...
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo WARNING: FFmpeg belum ditemukan.
    echo Fitur gambar tetap bisa dipakai.
    echo Fitur video butuh FFmpeg.
    echo.
    echo Install FFmpeg dengan command:
    echo winget install Gyan.FFmpeg
    echo.
) else (
    echo FFmpeg ditemukan.
)

echo.
echo Menjalankan Asset Converter...
echo.
python "App.py"

echo.
echo Aplikasi ditutup.
pause
endlocal
