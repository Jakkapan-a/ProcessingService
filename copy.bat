@REM COPY .env.example to .env
@REM This script is used to copy the .env.example file to .env
copy /Y .env.example .env >nul 2>&1
echo . 
echo .env file copied successfully.