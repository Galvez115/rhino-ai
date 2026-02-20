# Rhino AI - Arquitectura Técnica

## Visión General

Rhino AI es una aplicación web para pre-check de entregables técnicos con evaluación automática basada en rúbricas gubernamentales. El sistema NO modifica documentos, solo analiza y guía.

## Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Parsing**: python-docx para extracción de estructura DOCX
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **LLM**: OpenAI GPT-4 o Anthropic Claude (multi-provider)
- **Logging**: JSON structured logs con run_id

### Frontend
- **Framework**: React 18 + Vite
- **UI Pattern**: Wizard (Upload → Questions → Report)
- **Styling**: CSS vanilla (sin frameworks pesados)
- **API Client**: Axios

### Deploy
- **Containerización**: Docker + Docker Compose
- **Networking**: Expuesto en 0.0.0.0 para acceso LAN

## Arquitectura Backend

```
backend/
├── api/              # FastAPI routes y endpoints
├── services/         # Lógica de negocio
│   ├── classifier.py    # Clasificación de tipo de documento
│   └── evaluator.py     # Evaluación con rúbrica
├── domain/           # Modelos de dominio (Pydantic)
├── adapters/         # Adapters para LLM (OpenAI, Anthropic)
├── storage/          # Persistencia (SQLAlchemy)
├── utils/            # Utilidades (docx parser, config)
└── config/           # Configuración y rúbrica JSON
```

### Flujo de Evaluación

1. **Upload & Parse**
   - Usuario sube DOCX
   - `docx_parser.py` extrae estructura completa (títulos, secciones, tablas)
   - Genera `DocumentOutline` con metadata

2. **Clasificación**
   - `classifier.py` usa heurísticas determinísticas (keywords)
   - Si confianza < 0.4, usa LLM como desempate
   - Resultado: `DocumentType` + confidence

3. **Evaluación**
   - `evaluator.py` carga rúbrica del tipo detectado
   - Por cada criterio:
     - Busca evidencia en documento (keywords + location)
     - Usa LLM para evaluar estado (CUMPLE/PARCIAL/NO/NA)
     - Calcula puntos (NA excluye denominador)
   - Aplica penalizaciones (sin doble castigo)
   - Verifica fail-fast conditions

4. **Generación de Hallazgos**
   - Por cada criterio NO/PARCIAL:
     - Crea hallazgo con severidad
     - Genera recomendación detallada
     - Propone dónde insertar + ejemplo de texto
     - Calcula impacto estimado

5. **Preguntas Inteligentes**
   - Solo para gaps P0/P1/P2
   - Máximo 5 preguntas
   - Incluye: por_qué_importa, si_no_responde

6. **Re-evaluación**
   - Usuario responde preguntas
   - Respuestas se marcan como "evidencia_externa"
   - Re-evalúa criterios con nueva evidencia
   - Genera reporte final

## Reglas Anti-Alucinación

### Críticas
1. **Evidencia obligatoria**: Toda afirmación debe incluir `location + snippet`
2. **No inferir**: Si no hay evidencia → estado = NO
3. **NA justificado**: NA solo si criterio genuinamente no aplica
4. **Preguntas focalizadas**: Solo para gaps críticos
5. **Respuestas externas**: Marcadas como "evidencia_externa_al_documento"

### Fail-Fast
- **FF-01**: Documento < 100 palabras → RECHAZADO
- **FF-02**: Tipo UNKNOWN + confianza < 0.6 → REQUIERE_CORRECCION
- **FF-03**: Afirmaciones críticas sin evidencia → RECHAZADO
- **FF-04**: Contradicciones materiales → RECHAZADO

## Scoring

### Fórmula Base
```
score = (puntos_obtenidos / peso_aplicable) * 100
```

### Reglas
- **NA**: Excluye criterio del denominador (no suma ni al numerador ni denominador)
- **CUMPLE**: 100% del peso
- **PARCIAL**: 50% del peso
- **NO**: 0% del peso

### Penalizaciones
- Aplicadas DESPUÉS del score base
- NO se aplican si criterio ya está en 0 (evita doble castigo)
- Score final: `max(0, score + penalizaciones)`

### Decisión
```
if fail_fast_active:
    RECHAZADO
elif score >= 85 AND bloqueantes == 0:
    APROBADO
elif score >= 70:
    REQUIERE_CORRECCION
else:
    RECHAZADO
```

## LLM Adapters

### Interface Común
```python
class LLMInterface(ABC):
    async def generate(prompt, system_prompt, json_mode) -> str
    async def generate_json(prompt, system_prompt) -> dict
```

### Providers
- **OpenAI**: Usa `response_format={"type": "json_object"}`
- **Anthropic**: Extrae JSON de respuesta (maneja markdown)

### Guardrails
- Max tokens: 4000 (configurable)
- Temperatura: 0.1 (baja para consistencia)
- Timeout: 30s
- Retry: 3 intentos con backoff

## Base de Datos

### Modelos
- **Run**: Ejecución completa (id, filename, doc_type, score, decision, JSONs)
- **Question**: Preguntas y respuestas por run
- **Finding**: Hallazgos por run

### Migraciones
- SQLAlchemy con `create_all()` en startup
- Para producción: usar Alembic

## Frontend

### Componentes
- **UploadStep**: Drag & drop de DOCX
- **QuestionsStep**: Formulario de preguntas con prioridades
- **ReportStep**: Visualización de score, hallazgos, export

### Estado
- React useState para flujo wizard
- No usa Redux (MVP simple)
- API calls con Axios

### UX
- Stepper visual (1→2→3)
- Cards por severidad (bloqueante primero)
- Score potencial (actual, P0, P0+P1, todo)
- Export JSON y Markdown

## Seguridad

### Backend
- CORS configurado por env vars
- File upload: solo .docx, max 10MB
- SQL injection: protegido por SQLAlchemy ORM
- API keys: nunca en logs ni responses

### Frontend
- No almacena API keys
- Sanitización de inputs
- HTTPS recomendado en producción

## Performance

### Optimizaciones
- Parsing DOCX: streaming para archivos grandes
- LLM calls: paralelos cuando posible
- Database: índices en run_id
- Frontend: lazy loading de hallazgos

### Límites
- Max file size: 10MB
- Max sections: 100 (para LLM context)
- Max questions: 5
- Timeout LLM: 30s

## Deployment

### Local
```bash
docker-compose up --build
```

### Producción
1. Cambiar a PostgreSQL
2. Configurar reverse proxy (nginx)
3. HTTPS con Let's Encrypt
4. Variables de entorno seguras
5. Logs centralizados (ELK, CloudWatch)

### Escalabilidad
- Backend: stateless, puede escalar horizontalmente
- Database: connection pooling
- LLM: rate limiting por provider
- Storage: S3 para archivos en producción

## Testing

### Unit Tests
- `test_scoring.py`: Lógica de scoring (NA, penalizaciones)
- `test_fail_fast.py`: Condiciones fail-fast

### Integration Tests (TODO)
- Upload → Clasificación → Evaluación
- Re-evaluación con respuestas
- Export JSON/MD

### E2E Tests (TODO)
- Playwright para flujo completo

## Monitoreo

### Logs
- JSON structured logs
- Campos: run_id, doc_type, score, decision, timestamp
- Niveles: INFO, WARNING, ERROR

### Métricas (TODO)
- Tiempo de procesamiento por documento
- Tasa de fail-fast
- Distribución de scores
- Uso de LLM (tokens, costo)

## Roadmap

### MVP1 (Actual)
- ✅ Upload DOCX
- ✅ Clasificación automática
- ✅ Evaluación con rúbrica
- ✅ Hallazgos priorizados
- ✅ Preguntas inteligentes
- ✅ Export JSON/MD

### MVP2 (Futuro)
- [ ] Soporte para múltiples rúbricas
- [ ] Comparación de versiones de documentos
- [ ] Historial de evaluaciones
- [ ] Dashboard de métricas
- [ ] API pública con autenticación
- [ ] Webhooks para CI/CD

### MVP3 (Futuro)
- [ ] Sugerencias de texto con LLM
- [ ] Integración con Git (PR comments)
- [ ] Multi-idioma (i18n)
- [ ] Plantillas de documentos
- [ ] Colaboración en tiempo real
