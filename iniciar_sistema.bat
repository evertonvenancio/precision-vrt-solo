@echo off
cd /d C:\precision_vrt_solo
title Precision VRT Solo - Servidor
echo ========================================
echo   PRECISION VRT SOLO - INICIANDO...
echo ========================================
echo.
echo Aguarde 15 segundos, o navegador abrira na tela de login.
echo NAO FECHE ESTA JANELA!
echo.
start /b cmd /c "timeout /t 15 /nobreak >nul && start "" http://127.0.0.1:8000/auth/login"
python -m uvicorn main:app --reload
