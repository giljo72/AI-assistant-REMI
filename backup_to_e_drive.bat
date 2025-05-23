@echo off
echo ========================================
echo AI Assistant Backup Script
echo ========================================
echo.
echo Creating backup of F:\assistant to E:\root
echo Timestamp: %date% %time%
echo.

REM Create backup directory with timestamp
set "timestamp=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "backup_dir=E:\root\assistant_backup_%timestamp%"

echo Creating backup directory: %backup_dir%
mkdir "%backup_dir%"

echo.
echo Copying project files...
echo ========================================

REM Copy all project files excluding certain directories
robocopy "F:\assistant" "%backup_dir%" /E /XD node_modules venv venv_nemo __pycache__ .git nemo-models logs data\uploads data\models .pytest_cache dist build .next coverage /XF *.pyc *.log

echo.
echo ========================================
echo Backup completed to: %backup_dir%
echo.
echo To restore, simply copy all files from:
echo   %backup_dir%
echo back to:
echo   F:\assistant
echo ========================================
pause