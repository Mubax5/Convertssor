@echo off
title Asset Converter Installer

echo ========================================
echo Asset Converter - Auto Install & Run
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python belum terinstall atau belum masuk PATH.
    echo Install Python dulu dari https://www.python.org/downloads/
    echo Jangan lupa centang "Add python.exe to PATH" saat install.
    pause
    exit /b
)

echo Membuat virtual environment...
python -m venv .venv

echo.
echo Mengaktifkan virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Upgrade pip...
python -m pip install --upgrade pip

echo.
echo Install dependencies...
pip install pillow customtkinter pillow-avif-plugin

echo.
echo Cek FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: FFmpeg belum ditemukan.
    echo Fitur gambar tetap bisa jalan.
    echo Fitur video butuh FFmpeg.
    echo.
    echo Cara paling gampang install FFmpeg di Windows:
    echo 1. Install Winget/App Installer dari Microsoft Store kalau belum ada
    echo 2. Jalankan command:
    echo    winget install Gyan.FFmpeg
    echo.
) else (
    echo FFmpeg ditemukan.
)

echo.
echo Menjalankan Asset Converter...
python asset_converter_customtkinter.py

pause