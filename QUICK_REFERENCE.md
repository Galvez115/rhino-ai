# Rhino AI - Referencia Rápida

## 🚀 Inicio Rápido

```bash
# 1. Configurar
cp sample.env .env
# Editar .env y agregar API key

# 2. Iniciar
docker-compose up --build

# 3. Acceder
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📋 Comandos Comunes

### Docker

```bash
# Iniciar
docker-compose up

# Iniciar en background
docker-compose up -d

# Detener
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Rebuild
docker-compose up --build

# Limpiar todo
docker-compose down -v
```

### Desarrollo Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend
pytest tests/ -v
```

## 🔍 Debugging

```bash
# Ver logs backend
docker-compose logs -f backend

# Ver logs frontend
docker-compose logs -f frontend

# Entrar al container
docker-compose exec backend bash
docker-compose exec frontend sh

# Ver base de datos
sqlite3 backend/rhinoai.db
.tables
SELECT * FROM runs;
```

## 📡 API Endpoints

```bash
# Upload documento
curl -X POST http://localhost:8000/api/runs \
  -F "file=@documento.docx"

# Enviar respuestas
curl -X POST http://localhost:8000/api/runs/{run_id}/answers \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": "Q-1", "answer": "..."}]}'

# Obtener reporte
curl http://localhost:8000/api/runs/{run_id}

# Export JSON
curl http://localhost:8000/api/runs/{run_id}/export.json

# Export Markdown
curl http://localhost:8000/api/runs/{run_id}/export.md
```

## 🌐 Compartir con Equipo

### Opción 1: LAN
```bash
# Obtener IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Compartir
http://TU_IP:3000
```

### Opción 2: Tailscale
```bash
# 1. Instalar Tailscale
# 2. Obtener IP Tailscale (100.x.x.x)
# 3. Compartir: http://100.x.x.x:3000
```

### Opción 3: ngrok (temporal)
```bash
ngrok http 3000
# Compartir URL generada
```

## ⚙️ Variables de Entorno

```bash
# LLM
LLM_PROVIDER=openai|anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_TYPE=sqlite|postgres
DATABASE_URL=sqlite:///./rhinoai.db

# Backend
BACKEND_PORT=8000
UPLOAD_DIR=/tmp/rhino_uploads
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000
```

## 🧪 Testing

```bash
# Todos los tests
pytest tests/ -v

# Test específico
pytest tests/test_scoring.py -v

# Con cobertura
pytest tests/ --cov=. --cov-report=html
```

## 📊 Monitoreo

```bash
# Ver containers
docker ps

# Ver uso de recursos
docker stats

# Ver volúmenes
docker volume ls

# Ver redes
docker network ls
```

## 🔧 Troubleshooting

### Puerto ocupado
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :3000
kill -9 [PID]
```

### Limpiar Docker
```bash
# Limpiar containers detenidos
docker container prune

# Limpiar imágenes sin usar
docker image prune

# Limpiar todo
docker system prune -a
```

### Reiniciar desde cero
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 📝 Archivos Importantes

```
.env                    # Configuración (NO commitear)
rubrica_government.json # Rúbrica de evaluación
docker-compose.yml      # Orquestación
backend/main.py         # Entry point backend
frontend/src/App.jsx    # Entry point frontend
```

## 🎯 Flujo de Trabajo

```
1. Upload DOCX
   ↓
2. Clasificación automática
   ↓
3. Evaluación con rúbrica
   ↓
4. Preguntas (si hay gaps P0/P1/P2)
   ↓
5. Re-evaluación con respuestas
   ↓
6. Reporte final
   ↓
7. Export JSON/MD
```

## 🔐 Seguridad

```bash
# Nunca commitear
.env
*.db
uploads/

# Siempre validar
- Tipo de archivo (.docx only)
- Tamaño de archivo (< 10MB)
- API keys en .env
```

## 📚 Documentación

- **README.md**: Instalación y uso
- **ARCHITECTURE.md**: Diseño técnico
- **EXAMPLES.md**: Casos de uso
- **CONTRIBUTING.md**: Desarrollo
- **WINDOWS_SETUP.md**: Guía Windows
- **CHANGELOG.md**: Historial

## 🆘 Ayuda

```bash
# Validar setup
python validate-setup.py

# Ver versiones
docker --version
python --version
node --version

# Ver ayuda Docker
docker-compose --help

# Ver ayuda pytest
pytest --help
```

## 🎨 Personalización

### Cambiar puerto
```yaml
# docker-compose.yml
ports:
  - "8080:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Cambiar LLM provider
```bash
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Cambiar a PostgreSQL
```bash
# .env
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://user:pass@db:5432/rhinoai

# docker-compose.yml
# Descomentar servicio 'db'
```

## 📈 Performance

```bash
# Ver logs de performance
docker-compose logs backend | grep "run_id"

# Monitorear uso de memoria
docker stats

# Optimizar base de datos
sqlite3 rhinoai.db "VACUUM;"
```

## 🔄 Actualización

```bash
# Pull cambios
git pull

# Rebuild
docker-compose down
docker-compose up --build

# Migrar DB (si necesario)
# Ver CHANGELOG.md
```

## ✅ Checklist Pre-Deploy

- [ ] `.env` configurado con API key válida
- [ ] Docker Desktop corriendo
- [ ] Puertos 3000 y 8000 libres
- [ ] Firewall permite conexiones (si LAN)
- [ ] `python validate-setup.py` pasa
- [ ] Tests pasan: `pytest tests/ -v`

## 🎉 ¡Listo!

```bash
docker-compose up --build
# Abrir http://localhost:3000
# Subir documento DOCX
# Ver reporte
```
