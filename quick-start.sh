#!/bin/bash

echo "🦏 Rhino AI - Quick Start"
echo "=========================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No se encontró archivo .env"
    echo "Copiando sample.env a .env..."
    cp sample.env .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu API key"
    echo "   - Para OpenAI: OPENAI_API_KEY=sk-..."
    echo "   - Para Anthropic: ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    read -p "Presiona Enter cuando hayas configurado tu API key..."
fi

echo "🚀 Iniciando Rhino AI con Docker Compose..."
echo ""

docker-compose up --build

echo ""
echo "✅ Rhino AI está corriendo!"
echo ""
echo "Accede a:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
