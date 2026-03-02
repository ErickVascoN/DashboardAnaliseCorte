@echo off
title Dashboard Controle de Corte - Mantas
echo ============================================
echo   Dashboard Controle de Corte - Mantas
echo ============================================
echo.
echo Iniciando o dashboard...
echo O navegador abrira automaticamente.
echo.
cd /d "%~dp0"
".venv\Scripts\streamlit.exe" run dashboard.py --server.headless false
pause
