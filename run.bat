@echo off
title YouTranscribe - Streamlit
echo ======================================================================
echo                     YouTranscribe (Streamlit)
echo ======================================================================
echo.
echo  [1] Start Local Web App (http://localhost:8501) - [Default]
echo  [2] Start Local App + Public HTTPS Tunnel (Share with Phone/Web)
echo.
set /p choice="Choose an option [1 or 2, default is 1]: "

if "%choice%"=="2" (
    echo.
    echo Starting Streamlit in background...
    start "YouTranscribe Streamlit" cmd /k "python -m streamlit run app.py --server.port 8501 --server.headless true"
    echo Waiting for Streamlit to initialize...
    timeout /t 4 /nobreak >nul
    echo.
    echo Starting Public HTTPS Tunnel...
    npx localtunnel --port 8501
) else (
    echo.
    echo Starting Streamlit...
    python -m streamlit run app.py
)
pause
