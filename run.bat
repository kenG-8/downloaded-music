@echo off
chcp 65001 > nul
title MP3 320kbps Downloader (YouTube ^& TikTok)
cd /d "%~dp0"

python main.py %*

if "%~1"=="" (
    rem Double-clicked without arguments, already has interactive loop
) else (
    pause
)
