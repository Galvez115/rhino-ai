# Contribuir a Rhino AI

## Desarrollo Local

### Requisitos
- Python 3.11+
- Node.js 20+
- Docker y Docker Compose

### Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Setup Frontend

```bash
cd frontend
npm install
```

### Variables de Entorno

Copia `sample.env` a `.env` y configura:
- `LLM_PROVIDER`: openai o anthropic
- `OPENAI_API_KEY` o `ANTHROPIC_API_KEY`

### Ejecutar Tests

```bash
cd backend
pytest tests/ -v
```

### Ejecutar Localmente

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

## Estructura de Código

### Backend
- `api/`: Endpoints FastAPI
- `services/`: Lógica de negocio
- `domain/`: Modelos Pydantic
- `adapters/`: Integraciones externas (LLM)
- `storage/`: Persistencia
- `utils/`: Utilidades

### Frontend
- `components/`: Componentes React
- `services/`: API client
- `App.jsx`: Componente principal

## Convenciones

### Python
- PEP 8 style guide
- Type hints obligatorios
- Docstrings en funciones públicas
- Logging con structured JSON

### JavaScript
- ES6+ syntax
- Functional components (React)
- PropTypes o TypeScript (futuro)

### Git
- Commits descriptivos en español
- Branch naming: `feature/nombre`, `fix/nombre`
- PR con descripción y tests

## Testing

### Unit Tests
- Cobertura mínima: 70%
- Tests para lógica crítica (scoring, fail-fast)
- Mocks para LLM calls

### Integration Tests
- Flujo completo: upload → evaluación → export
- Database en memoria (SQLite)

## Agregar Nuevo Tipo de Documento

1. Editar `rubrica_government.json`:
   ```json
   "NUEVO_TIPO": {
     "nombre": "...",
     "keywords": [...],
     "criterios": [...]
   }
   ```

2. Actualizar `DocumentType` en `domain/models.py`

3. Agregar tests en `tests/test_classifier.py`

## Agregar Nuevo LLM Provider

1. Crear adapter en `adapters/nuevo_provider.py`:
   ```python
   class NuevoProviderAdapter(LLMInterface):
       async def generate(...):
           ...
   ```

2. Registrar en `adapters/llm_factory.py`

3. Agregar config en `utils/config.py`

4. Documentar en README

## Debugging

### Backend Logs
```bash
docker-compose logs -f backend
```

### Frontend Console
- Abrir DevTools en navegador
- Ver Network tab para API calls

### Database
```bash
sqlite3 backend/rhinoai.db
.tables
SELECT * FROM runs;
```

## Performance

### Profiling Backend
```python
import cProfile
cProfile.run('evaluator.evaluate()')
```

### Profiling Frontend
- React DevTools Profiler
- Lighthouse en Chrome

## Seguridad

### Checklist
- [ ] No exponer API keys en logs
- [ ] Validar inputs (file type, size)
- [ ] Sanitizar outputs
- [ ] HTTPS en producción
- [ ] Rate limiting en API

## Release

### Versioning
- Semantic versioning: MAJOR.MINOR.PATCH
- Tag en Git: `v1.0.0`

### Changelog
- Mantener CHANGELOG.md actualizado
- Formato: Keep a Changelog

### Deploy
1. Tests pasan
2. Build Docker images
3. Tag y push a registry
4. Deploy con docker-compose
5. Smoke tests en producción

## Soporte

- Issues: GitHub Issues
- Discusiones: GitHub Discussions
- Email: [tu-email]

## Licencia

Uso interno - MVP1
