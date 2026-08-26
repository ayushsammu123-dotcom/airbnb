@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Airbnb Analytics - Push to GitHub
echo ============================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/airbnb-analytics.git): "

if "%REPO_URL%"=="" (
    echo Error: No repository URL provided. Exiting.
    pause
    exit /b 1
)

echo.
echo [1/5] Initializing git repository...
git init

echo [2/5] Staging files...
git add .

echo [3/5] Creating initial commit...
git commit -m "feat: Airbnb Pricing & Revenue Analytics Platform (Delhi NCR)"

echo [4/5] Setting main branch...
git branch -M main

echo [5/5] Adding remote and pushing to GitHub...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ============================================================
echo   Successfully pushed to GitHub!
echo   Deploy at https://share.streamlit.io with dashboard/app.py
echo ============================================================
pause
