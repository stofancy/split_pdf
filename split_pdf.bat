@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.7 or higher.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed! Please install pip.
    pause
    exit /b 1
)

:: Check if requirements are installed
if not exist "%~dp0\requirements_installed" (
    echo Installing required packages...
    pip install -r "%~dp0\requirements.txt"
    if errorlevel 1 (
        echo Failed to install requirements!
        pause
        exit /b 1
    )
    echo. > "%~dp0\requirements_installed"
)

:: If no arguments provided, show usage
if "%~1"=="" (
    echo Usage: split_pdf.bat input_file.pdf output_file.pdf [--splits 2^|3] [--batch-size NUMBER]
    echo.
    echo Example:
    echo     split_pdf.bat input.pdf output.pdf --splits 3 --batch-size 5
    echo.
    echo Options:
    echo     --splits     Number of parts to split each page into ^(2 or 3^)
    echo     --batch-size Number of pages to process in parallel
    pause
    exit /b 1
)

:: Run the Python script with all arguments
python "%~dp0\split_pdf.py" %*

if errorlevel 1 (
    echo An error occurred while processing the PDF.
    pause
    exit /b 1
)

echo PDF processing completed successfully!
pause
exit /b 0
