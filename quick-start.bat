@echo off
echo 🦏 Rhino AI - Quick Start
echo ==========================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  No se encontró archivo .env
    echo Copiando sample.env a .env...
    copy sample.env .env
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env y agrega tu API key
    echo    - Para OpenAI: OPENAI_API_KEY=sk-...
    echo    - Para Anthropic: ANTHROPIC_API_KEY=sk-ant-...
    echo.
    pause
)

echo 🚀 Iniciando Rhino AI con Docker Compose...
echo.

docker-compose up --build

echo.
echo ✅ Rhino AI está corriendo!
echo.
echo Accede a:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
pause
