@echo off
echo Starting ChatGPT Clone with RAG Code Assistant...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your Groq API key
    echo.
    echo Example:
    echo   copy .env.example .env
    echo   edit .env and add: GROQ_API_KEY=your_actual_api_key_here
    echo.
    pause
    exit /b 1
)

echo Building and starting containers...
docker-compose up --build

pause
