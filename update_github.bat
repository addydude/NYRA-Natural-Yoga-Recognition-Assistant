@echo off
REM Github update script
echo.
echo Updating GitHub repository...
echo.

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Add all files
echo Adding files to git...
git add .

REM Commit changes
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg="Updated project with WebSocket fixes and improved documentation"

echo.
echo Committing with message: %commit_msg%
git commit -m "%commit_msg%"

REM Push to remote
echo.
echo Pushing to GitHub...
git push

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to push to GitHub. Check your credentials and connection.
    echo You might need to set up your GitHub credentials first with:
    echo git config --global user.email "your-email@example.com"
    echo git config --global user.name "Your Name"
) else (
    echo.
    echo Successfully updated GitHub repository!
)

pause
