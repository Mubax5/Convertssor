@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Asset Converter - Installer

echo ====================================================
echo Asset Converter - Install Python, FFmpeg, and Run App
echo ====================================================
echo.

REM ====================================================
REM CONFIG
REM ====================================================
set "APP_FILE=App.py"
set "VENV_DIR=.venv"
set "PYTHON_WINGET_ID=Python.Python.3.12"
set "FFMPEG_WINGET_ID=Gyan.FFmpeg"

REM ====================================================
REM CHECK APP FILE
REM ====================================================
if not exist "%APP_FILE%" (
    echo ERROR: %APP_FILE% tidak ditemukan.
    echo Taruh install.bat ini satu folder dengan %APP_FILE%.
    echo.
    pause
    exit /b 1
)

REM ====================================================
REM CHECK WINGET
REM ====================================================
where winget >nul 2>nul
if errorlevel 1 (
    echo ERROR: Winget tidak ditemukan di Windows ini.
    echo.
    echo Solusi:
    echo 1. Buka Microsoft Store
    echo 2. Install / update "App Installer"
    echo 3. Jalankan ulang install.bat
    echo.
    pause
    exit /b 1
)

REM ====================================================
REM FIND PYTHON
REM ====================================================
set "PY_CMD="

where python >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo Python belum ditemukan. Menginstall Python...
    echo.
    winget install --id %PYTHON_WINGET_ID% -e --scope user --accept-package-agreements --accept-source-agreements

    if errorlevel 1 (
        echo.
        echo Gagal install Python via winget.
        echo Coba jalankan Command Prompt sebagai Administrator, lalu ulangi install.bat.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Python berhasil diinstall. Mencari lokasi Python...

    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        where python >nul 2>nul
        if not errorlevel 1 (
            set "PY_CMD=python"
        ) else (
            where py >nul 2>nul
            if not errorlevel 1 (
                set "PY_CMD=py -3"
            )
        )
    )
)

if "%PY_CMD%"=="" (
    echo.
    echo ERROR: Python sudah diinstall, tapi belum bisa dipanggil dari terminal ini.
    echo Tutup terminal ini, lalu double click install.bat lagi.
    echo.
    pause
    exit /b 1
)

echo Python siap: %PY_CMD%
echo.

REM ====================================================
REM INSTALL FFMPEG
REM ====================================================
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo FFmpeg belum ditemukan. Menginstall Gyan.FFmpeg...
    echo.
    winget install --id %FFMPEG_WINGET_ID% -e --accept-package-agreements --accept-source-agreements

    if errorlevel 1 (
        echo.
        echo WARNING: Gagal install Gyan.FFmpeg via winget.
        echo Aplikasi tetap bisa jalan untuk fitur gambar.
        echo Fitur video butuh FFmpeg.
        echo.
    ) else (
        echo.
        echo Gyan.FFmpeg berhasil diinstall.
        echo Jika fitur video masih belum aktif, restart terminal / PC lalu jalankan ulang install.bat.
        echo.
    )
) else (
    echo FFmpeg sudah tersedia.
    echo.
)

REM ====================================================
REM CREATE VENV
REM ====================================================
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Membuat virtual environment...
    %PY_CMD% -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo.
        echo ERROR: Gagal membuat virtual environment.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment sudah ada.
)

echo.
echo Mengaktifkan virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

if errorlevel 1 (
    echo.
    echo ERROR: Gagal mengaktifkan virtual environment.
    echo.
    pause
    exit /b 1
)

REM ====================================================
REM INSTALL PYTHON DEPENDENCIES
REM ====================================================
echo.
echo Menginstall / update dependency Python...
python -m pip install --upgrade pip
python -m pip install customtkinter pillow pillow-avif-plugin

if errorlevel 1 (
    echo.
    echo ERROR: Gagal install dependency Python.
    echo Cek koneksi internet, lalu jalankan ulang install.bat.
    echo.
    pause
    exit /b 1
)

REM ====================================================
REM RUN APP
REM ====================================================
echo.
echo ====================================================
echo Instalasi selesai. Menjalankan Asset Converter...
echo ====================================================
echo.

python "%APP_FILE%"

echo.
echo Aplikasi ditutup.
pause
endlocal
