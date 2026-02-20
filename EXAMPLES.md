# Rhino AI - Ejemplos de Uso

## Ejemplo 1: Documento DTM (Migración)

### Documento de Entrada
Un documento DOCX con:
- Título: "Plan de Migración Base de Datos Oracle a PostgreSQL"
- Secciones:
  - Alcance y objetivos
  - Inventario de datos
  - Estrategia de migración
  - Plan de rollback
  - Cronograma

### Resultado Esperado
- **Tipo detectado**: DTM
- **Score**: 75-85 (si tiene la mayoría de secciones)
- **Decisión**: REQUIERE_CORRECCION o APROBADO
- **Hallazgos típicos**:
  - Falta plan de validación detallado (P1)
  - Roles y responsabilidades incompletos (P2)
  - Gestión de riesgos sin mitigación (P1)

### Preguntas que Rhino AI haría
1. **[P0]** ¿Puede proporcionar el procedimiento de rollback detallado?
   - Por qué importa: Criterio bloqueante, 15 puntos de impacto
   - Si no responde: Se evaluará como NO, posible RECHAZADO

2. **[P1]** ¿Cuáles son los casos de prueba para validar la migración?
   - Por qué importa: Criterio mayor, 15 puntos de impacto
   - Si no responde: Score reducido, REQUIERE_CORRECCION

## Ejemplo 2: Documento DSP (Solución Propuesta)

### Documento de Entrada
- Título: "Propuesta: Sistema de Gestión de Inventario"
- Secciones:
  - Contexto y problemática
  - Requisitos funcionales
  - Arquitectura (con diagramas)
  - Modelo de datos
  - Seguridad

### Resultado Esperado
- **Tipo detectado**: DSP
- **Score**: 80-90
- **Decisión**: APROBADO o REQUIERE_CORRECCION
- **Hallazgos típicos**:
  - Requisitos no funcionales sin métricas (P1)
  - Estimación de costos faltante (P2)
  - Plan de implementación sin cronograma (P1)

### Recomendaciones de Rhino AI
```
Hallazgo: [P1] Requisitos no funcionales
Severidad: mayor
Evidencia: No se encontró sección de RNF

Recomendación: Agregar sección de Requisitos No Funcionales con métricas específicas

Qué agregar:
- Performance: tiempo de respuesta < 200ms
- Disponibilidad: 99.9% uptime
- Escalabilidad: soportar 10,000 usuarios concurrentes
- Seguridad: autenticación OAuth2, cifrado AES-256

Dónde insertar: Después de "Requisitos Funcionales", antes de "Arquitectura"

Ejemplo de texto:
## 3. Requisitos No Funcionales

### 3.1 Performance
- Tiempo de respuesta API: < 200ms (p95)
- Tiempo de carga UI: < 2s
- Throughput: 1000 req/s

### 3.2 Disponibilidad
- SLA: 99.9% uptime mensual
- RTO: 1 hora
- RPO: 15 minutos

Impacto estimado: +10 puntos
```

## Ejemplo 3: Documento con Fail-Fast

### Documento de Entrada
- Archivo DOCX con solo 50 palabras
- Sin estructura clara

### Resultado
```json
{
  "fail_fast": [
    {
      "code": "FF-01",
      "name": "Documento vacío o ilegible",
      "active": true,
      "evidencia": "Word count: 50",
      "explicacion": "El documento no contiene contenido suficiente"
    }
  ],
  "decision": "RECHAZADO",
  "score": 0
}
```

## Ejemplo 4: Documento UNKNOWN

### Documento de Entrada
- Título: "Notas de Reunión"
- Contenido genérico sin keywords específicos

### Resultado
- **Tipo detectado**: UNKNOWN
- **Confianza**: 0.2
- **Decisión**: REQUIERE_CORRECCION (por FF-02)
- **Mensaje**: "No se pudo determinar el tipo de entregable con suficiente confianza"

### Acción Recomendada
- Revisar el título y contenido
- Agregar keywords específicos del tipo de documento
- Re-subir con estructura más clara

## Ejemplo 5: Flujo Completo con Preguntas

### Paso 1: Upload
```
POST /api/runs
File: plan_migracion.docx

Response:
{
  "run_id": "abc-123",
  "doc_type": "DTM",
  "preliminary_evaluation": {
    "score": 65,
    "decision": "REQUIERE_CORRECCION"
  },
  "preguntas": [
    {
      "id": "Q-DTM-04",
      "pregunta": "¿Puede proporcionar información sobre: Plan de rollback?",
      "prioridad": "P0",
      "por_que_importa": "Criterio bloqueante, 15 puntos de impacto"
    }
  ]
}
```

### Paso 2: Responder Preguntas
```
POST /api/runs/abc-123/answers
{
  "answers": [
    {
      "question_id": "Q-DTM-04",
      "answer": "El plan de rollback incluye: 1) Backup completo pre-migración, 2) Scripts de reversión automáticos, 3) Validación de integridad post-rollback, 4) Tiempo estimado: 2 horas"
    }
  ]
}

Response:
{
  "score": 78,
  "decision": "REQUIERE_CORRECCION",
  "score_potencial": {
    "actual": 78,
    "si_corrige_p0": 85,
    "si_corrige_p0_p1": 92,
    "si_corrige_todo": 95
  }
}
```

### Paso 3: Ver Reporte
```
GET /api/runs/abc-123

Response: Reporte completo con hallazgos priorizados
```

### Paso 4: Export
```
GET /api/runs/abc-123/export.md

Descarga: reporte_abc-123.md
```

## Ejemplo 6: Score Potencial

### Escenario
- Score actual: 72
- Hallazgos:
  - 2 bloqueantes (P0): +13 puntos cada uno
  - 3 mayores (P1): +8 puntos cada uno
  - 5 menores (P2): +2 puntos cada uno

### Cálculo
```
Actual: 72

Si corrige P0:
72 + (2 × 13) = 98

Si corrige P0 + P1:
72 + (2 × 13) + (3 × 8) = 122 → 100 (cap)

Si corrige todo:
72 + (2 × 13) + (3 × 8) + (5 × 2) = 132 → 100 (cap)
```

### Visualización en UI
```
┌─────────────────────────────────────┐
│ Score Potencial                     │
├─────────────────────────────────────┤
│ Actual:           72                │
│ Si corrige P0:    98  ⬆️ +26        │
│ Si corrige P0+P1: 100 ⬆️ +28        │
│ Si corrige todo:  100 ⬆️ +28        │
└─────────────────────────────────────┘
```

## Ejemplo 7: Evidencia en Hallazgos

### Hallazgo con Evidencia Encontrada
```json
{
  "id": "H-DTM-03-a1b2c3",
  "titulo": "Estrategia de migración",
  "severidad": "mayor",
  "evidencia_tipo": "found",
  "evidencia_detalle": "Section 3.1: ...utilizaremos un enfoque de migración por fases...",
  "recomendacion": "Completar la estrategia con herramientas y scripts específicos"
}
```

### Hallazgo sin Evidencia
```json
{
  "id": "H-DTM-04-d4e5f6",
  "titulo": "Plan de rollback",
  "severidad": "bloqueante",
  "evidencia_tipo": "missing",
  "evidencia_detalle": "No se encontró evidencia en el documento",
  "recomendacion": "Agregar sección completa de Plan de Rollback",
  "que_agregar": "Procedimiento detallado, criterios de activación, pasos, tiempos",
  "donde_insertar": "Después de 'Estrategia de migración', antes de 'Cronograma'",
  "ejemplo_texto": "## 4. Plan de Rollback\n\n### 4.1 Criterios de Activación\n..."
}
```

## Ejemplo 8: Uso de API Directa

### cURL
```bash
# Upload
curl -X POST http://localhost:8000/api/runs \
  -F "file=@documento.docx"

# Submit answers
curl -X POST http://localhost:8000/api/runs/abc-123/answers \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": "Q-1", "answer": "..."}]}'

# Get report
curl http://localhost:8000/api/runs/abc-123

# Export JSON
curl http://localhost:8000/api/runs/abc-123/export.json > report.json

# Export Markdown
curl http://localhost:8000/api/runs/abc-123/export.md > report.md
```

### Python
```python
import requests

# Upload
with open("documento.docx", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/runs",
        files={"file": f}
    )
run_data = response.json()

# Submit answers
answers = {
    "answers": [
        {"question_id": "Q-1", "answer": "Mi respuesta"}
    ]
}
response = requests.post(
    f"http://localhost:8000/api/runs/{run_data['run_id']}/answers",
    json=answers
)
evaluation = response.json()

print(f"Score: {evaluation['score']}")
print(f"Decisión: {evaluation['decision']}")
```

## Ejemplo 9: Integración CI/CD

### GitHub Actions
```yaml
name: Document Check

on:
  pull_request:
    paths:
      - 'docs/**/*.docx'

jobs:
  rhino-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check documents
        run: |
          for doc in docs/**/*.docx; do
            curl -X POST http://rhino-ai.internal/api/runs \
              -F "file=@$doc" \
              -o result.json
            
            score=$(jq -r '.preliminary_evaluation.score' result.json)
            decision=$(jq -r '.preliminary_evaluation.decision' result.json)
            
            if [ "$decision" = "RECHAZADO" ]; then
              echo "❌ $doc: RECHAZADO (score: $score)"
              exit 1
            fi
          done
```

## Tips y Mejores Prácticas

### Para Mejores Resultados
1. **Estructura clara**: Usa headings (Heading 1, 2, 3)
2. **Keywords**: Incluye términos específicos del tipo de documento
3. **Tablas**: Usa tablas para datos estructurados
4. **Evidencia**: Sé específico, incluye números y métricas
5. **Completitud**: Cubre todos los criterios de la rúbrica

### Errores Comunes
1. ❌ Documento sin estructura (solo texto plano)
2. ❌ Títulos genéricos ("Introducción", "Conclusión")
3. ❌ Afirmaciones sin evidencia ("El sistema es seguro")
4. ❌ Falta de detalles técnicos
5. ❌ Contradicciones entre secciones

### Optimización de Score
1. Revisa la rúbrica del tipo de documento
2. Asegúrate de cubrir criterios bloqueantes (P0)
3. Incluye evidencia específica con métricas
4. Usa tablas para información estructurada
5. Responde las preguntas de Rhino AI con detalle
