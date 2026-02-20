# Rhino AI - Pre-check de Entregables

MVP1 de análisis automático de documentos DOCX con evaluación por rúbrica gubernamental.

## Características

- Upload de archivos DOCX con extracción completa de estructura
- Clasificación automática de tipo de entregable (DTM, DSP, DTC, DoD, etc.)
- Evaluación con rúbrica exacta: criterios, pesos, severidades, fail-fast
- Generación de hallazgos priorizados con evidencia y recomendaciones
- Preguntas inteligentes solo para gaps críticos (P0/P1/P2)
- Score actual + potencial con decisión (APROBADO/REQUIERE_CORRECCION/RECHAZADO)
- Export JSON y Markdown

## Stack Técnico

- Backend: Python 3.11 + FastAPI + python-docx + SQLite
- Frontend: React + Vite
- Deploy: Docker Compose
- LLM: OpenAI (GPT) o Anthropic (Claude) configurable

## Requisitos Previos

- Docker y Docker Compose
- API Key de OpenAI o Anthropic

## Instalación y Ejecución Local

### 1. Clonar y configurar

```bash
# Copiar variables de entorno
cp sample.env .env

# Editar .env y agregar tu API key
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

### 2. Levantar con Docker Compose

```bash
docker-compose up --build
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Docs API: http://localhost:8000/docs

### 3. Desarrollo sin Docker

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Exponer a Compañeros de Equipo

### Opción 1: Red Local (LAN)

1. Obtén tu IP local:
   - Windows: `ipconfig` (buscar IPv4)
   - Linux/Mac: `ifconfig` o `ip addr`

2. Asegúrate que docker-compose expone los puertos correctamente (ya configurado)

3. Comparte con tu equipo:
   - Frontend: `http://TU_IP:3000`
   - Backend: `http://TU_IP:8000`

4. Firewall: permite conexiones entrantes en puertos 3000 y 8000

### Opción 2: Tailscale (VPN mesh, gratis)

1. Instala Tailscale: https://tailscale.com/download
2. Inicia sesión en todos los dispositivos
3. Comparte tu IP de Tailscale (ej: `100.x.x.x`)
4. Acceso: `http://100.x.x.x:3000`

### Opción 3: Cloudflare Tunnel (gratis, público)

1. Instala cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
2. Autentícate: `cloudflared tunnel login`
3. Crea túnel:
   ```bash
   cloudflared tunnel create rhino-ai
   cloudflared tunnel route dns rhino-ai rhino-ai.tudominio.com
   ```
4. Configura `config.yml` para apuntar a localhost:3000
5. Ejecuta: `cloudflared tunnel run rhino-ai`

### Opción 4: ngrok (rápido, temporal)

```bash
ngrok http 3000
# Comparte la URL pública generada
```

## Cambiar a PostgreSQL

1. Edita `.env`:
```env
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://user:pass@db:5432/rhinoai
```

2. Descomenta el servicio `db` en `docker-compose.yml`

3. Reinicia: `docker-compose up --build`

## Estructura de Archivos

```
backend/
├── api/          # Endpoints FastAPI
├── services/     # Lógica de negocio (evaluación, scoring)
├── domain/       # Modelos de dominio
├── adapters/     # LLM adapters (OpenAI, Anthropic)
├── storage/      # Persistencia (SQLite/Postgres)
├── utils/        # Utilidades (docx parser, logs)
└── config/       # Configuración y rúbrica

frontend/
├── src/
│   ├── components/  # UI components
│   ├── pages/       # Wizard steps
│   ├── services/    # API client
│   └── App.jsx
```

## Testing

```bash
cd backend
pytest tests/ -v
```

Tests incluidos:
- Scoring con NA (excluye denominador)
- Penalizaciones sin doble castigo
- Fail-fast triggers

## API Endpoints

- `POST /api/runs` - Upload DOCX, retorna run_id + outline + score preliminar + preguntas
- `POST /api/runs/{run_id}/answers` - Enviar respuestas, re-evaluar
- `GET /api/runs/{run_id}` - Estado y reporte completo
- `GET /api/runs/{run_id}/export.json` - Export JSON
- `GET /api/runs/{run_id}/export.md` - Export Markdown

## Flujo de Usuario

1. **Upload**: Subir archivo DOCX
2. **Questions**: Responder preguntas críticas (P0/P1/P2)
3. **Report**: Ver hallazgos por severidad con evidencia
4. **Checklist**: Plan de corrección priorizado

## Logs

Los logs incluyen `run_id` para trazabilidad:
```bash
docker-compose logs -f backend
```

## Troubleshooting

- **Error de API Key**: Verifica `.env` y reinicia containers
- **Puerto ocupado**: Cambia puertos en `docker-compose.yml`
- **Memoria insuficiente**: Ajusta `LLM_MAX_TOKENS` en `.env`

## Licencia

Uso interno - MVP1
