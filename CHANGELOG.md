# Changelog

Todos los cambios notables en Rhino AI serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1.0] - 2026-02-20 - MVP1.1 Hotfix

### Cambiado - Detector Determinístico
- **BREAKING**: Reemplazado clasificador heurístico+LLM por detector determinístico basado en JSON de Gobierno
- Nuevo módulo `backend/services/doc_type_detector.py` con reglas exactas
- Nuevo archivo de configuración `backend/config/document_type_detection_rhino.json`
- LLM ahora solo se usa como desempate en empates ±5 puntos entre candidatos válidos

### Agregado
- Sistema de scoring 0-100 con pesos configurables por señal
- Detección de indicadores fuertes (headings, tables, keywords)
- Patrones estructurales específicos por tipo de documento
- Reglas de dominancia estructural (matriz RF↔TC => DTM, etc.)
- Resolución de conflictos típicos (DTM vs PLAN, DSP vs DTC, RUNBOOK vs DTC, RCA vs RUNBOOK)
- Detección de conflicto nombre vs contenido (>15 puntos + >=2 indicadores fuertes)
- Manejo de UNKNOWN con preguntas para clasificar
- Top 3 candidatos con scores y evidencia
- UI: Sección "Detección de Tipo de Documento" en reporte
- UI: Banner de conflicto nombre vs contenido
- UI: Preguntas para clasificar si UNKNOWN
- Tests unitarios completos para detector (8 escenarios)

### Mejorado
- Confianza de detección más precisa basada en evidencia
- Trazabilidad completa: cada señal tiene evidencia (location + snippet)
- Razón detallada de por qué se seleccionó cada tipo
- Secondary signals para análisis adicional

### Técnico
- `extract_features()`: Extrae características del documento
- `has_at_least_one_strong_indicator()`: Valida indicadores fuertes
- `check_structural_patterns()`: Detecta patrones estructurales
- `score_each_type()`: Calcula score 0-100 por tipo
- `select_type()`: Selecciona tipo final con reglas de Gobierno
- API: `detection_result` incluido en response de `/api/runs`
- Frontend: `detectionResult` prop en ReportStep

### Tests
- ✅ DTM vs PLAN_PRUEBAS (matriz RF↔TC => DTM)
- ✅ PLAN_PRUEBAS (pasos/datos/resultados)
- ✅ DSP vs DTC (APIs/endpoints => DTC)
- ✅ DSP (escenarios/reglas negocio)
- ✅ RUNBOOK vs DTC (ventanas/monitoreo => RUNBOOK)
- ✅ RCA vs RUNBOOK (timeline/causa raíz => RCA)
- ✅ Conflicto nombre vs contenido (>15 + >=2 fuertes)
- ✅ UNKNOWN sin umbral o sin indicadores

## [1.1.0] - 2026-02-20

### Agregado - MVP1.1 (Hotfix/Iteración)
- **Detector determinístico de tipo de documento** basado en `document_type_detection_rhino.json`
  - Scoring 0-100 con pesos exactos por señal
  - Umbrales por tipo de documento
  - Indicadores fuertes (headings, tables, keywords)
  - Patrones estructurales
  - Reglas de dominancia estructural
  - Resolución de conflictos típicos (DTM vs PLAN_PRUEBAS, DSP vs DTC, etc.)
  - Política de conflicto nombre vs contenido
  - Manejo de UNKNOWN con preguntas para clasificar
- **Top 3 candidatos** con scores y evidencia
- **Detección de conflicto nombre vs contenido**
  - Se activa si diferencia > 15 puntos y contenido tiene ≥ 2 indicadores fuertes
  - Genera hallazgo MAYOR "Control documental" (P1)
  - Banner visual en UI
- **Visualización mejorada en UI**
  - Sección "Detección de Tipo de Documento" con:
    - Tipo detectado, confianza, razón
    - Top 3 candidatos con scores
    - Banner de conflicto (si aplica)
    - Preguntas para clasificar (si UNKNOWN)
    - Señales secundarias
- **LLM solo como desempate** en empates ±5 puntos (antes se usaba siempre)
- **Tests unitarios** para detector (12 tests)
  - DTM vs PLAN_PRUEBAS con matriz trazabilidad
  - DSP vs DTC con APIs/endpoints
  - RUNBOOK vs DTC con ventanas/monitoreo
  - RCA vs RUNBOOK con timeline/causa raíz
  - Conflicto nombre vs contenido
  - UNKNOWN sin umbral o sin indicadores

### Cambiado
- Reemplazado `classifier.py` (heurística + LLM) por `doc_type_detector.py` (determinístico)
- Agregado campo `detection_result_json` a modelo Run en base de datos
- Actualizado `evaluator.py` para aceptar `detection_result` y generar hallazgo de conflicto
- Actualizado `routes.py` para usar nuevo detector y guardar `detection_result`
- Actualizado `App.jsx` y `ReportStep.jsx` para mostrar información de detección

### Técnico
- Nuevo archivo: `backend/config/document_type_detection_rhino.json` (configuración completa)
- Nuevo archivo: `backend/services/doc_type_detector.py` (detector determinístico)
- Nuevo archivo: `backend/tests/test_doc_type_detector.py` (12 tests unitarios)
- Modificado: `backend/api/routes.py` (integración con detector)
- Modificado: `backend/services/evaluator.py` (hallazgo de conflicto)
- Modificado: `backend/storage/database.py` (campo detection_result_json)
- Modificado: `frontend/src/App.jsx` (estado detectionResult)
- Modificado: `frontend/src/components/ReportStep.jsx` (visualización detección)

### Reglas Implementadas
- **Candidato válido**: score >= threshold AND has_at_least_one_strong_indicator
- **Desempate**: dominancia estructural > conflictos típicos > filename > score
- **Conflicto nombre vs contenido**: gana contenido si diferencia > 15 y ≥ 2 indicadores fuertes
- **UNKNOWN**: si ningún tipo supera umbral o tiene indicadores fuertes

## [1.0.0] - 2026-02-20

### Agregado - MVP1
- Upload de archivos DOCX con extracción completa de estructura
- Clasificación automática de tipo de documento (DTM, DSP, DTC, DoD, etc.)
  - Heurísticas determinísticas basadas en keywords
  - LLM como desempate para casos ambiguos
- Evaluación con rúbrica gubernamental exacta
  - Criterios con pesos y severidades
  - Estados: CUMPLE, PARCIAL, NO, NA (excluye denominador)
  - Penalizaciones sin doble castigo
- Sistema fail-fast con 4 condiciones críticas
  - FF-01: Documento vacío (< 100 palabras)
  - FF-02: Tipo no identificable
  - FF-03: Afirmaciones sin evidencia
  - FF-04: Contradicciones materiales
- Generación de hallazgos priorizados
  - Severidad: bloqueante, mayor, menor, sugerencia
  - Evidencia: found, missing, inconsistent
  - Recomendaciones detalladas con ejemplos
  - Impacto estimado en puntos
- Preguntas inteligentes solo para gaps P0/P1/P2
  - Máximo 5 preguntas
  - Contexto: por qué importa, qué pasa si no responde
- Score potencial (actual, P0, P0+P1, todo)
- Decisión automática: APROBADO / REQUIERE_CORRECCION / RECHAZADO
- Export de reportes en JSON y Markdown
- UI wizard con 3 pasos: Upload → Questions → Report
- Soporte multi-proveedor LLM (OpenAI GPT-4, Anthropic Claude)
- Base de datos SQLite (default) con opción PostgreSQL
- Docker Compose para deploy local
- Logs estructurados JSON con run_id
- Tests unitarios para scoring y fail-fast
- Documentación completa:
  - README con instrucciones de instalación y deploy
  - ARCHITECTURE con detalles técnicos
  - EXAMPLES con casos de uso
  - CONTRIBUTING con guía de desarrollo

### Características Técnicas
- Backend: Python 3.11 + FastAPI
- Frontend: React 18 + Vite
- Parsing: python-docx con extracción de secciones, tablas, metadata
- LLM: Adapters con interface común, guardrails (max tokens, temperatura)
- Database: SQLAlchemy async con soporte SQLite/PostgreSQL
- Reglas anti-alucinación:
  - Evidencia obligatoria (location + snippet)
  - No inferir contenido faltante
  - NA solo con justificación
  - Respuestas de usuario marcadas como "evidencia_externa"

### Seguridad
- CORS configurable por environment
- Validación de tipo de archivo (.docx only)
- API keys nunca en logs ni responses
- SQL injection protegido por ORM

### Performance
- Parsing streaming para archivos grandes
- LLM calls con timeout y retry
- Database con índices en run_id
- Frontend con lazy loading

## [Unreleased]

### Planeado para MVP2
- Soporte para múltiples rúbricas personalizadas
- Comparación de versiones de documentos
- Historial de evaluaciones por documento
- Dashboard de métricas y analytics
- API pública con autenticación JWT
- Webhooks para integración CI/CD
- Rate limiting por usuario/IP
- Cache de evaluaciones

### Planeado para MVP3
- Sugerencias de texto generadas por LLM
- Integración con Git (comentarios en PRs)
- Multi-idioma (i18n) - inglés, español
- Plantillas de documentos por tipo
- Colaboración en tiempo real
- Notificaciones por email/Slack
- Exportación a PDF con branding
- API GraphQL

## Notas de Versión

### Compatibilidad
- Python 3.11+
- Node.js 20+
- Docker 20+
- Navegadores modernos (Chrome 90+, Firefox 88+, Safari 14+)

### Migraciones
- v1.0.0: Primera versión, no requiere migración

### Deprecaciones
- Ninguna en v1.0.0

### Problemas Conocidos
- [ ] Archivos DOCX muy grandes (>50MB) pueden causar timeout
- [ ] Tablas complejas con merge cells pueden no parsearse correctamente
- [ ] LLM puede ocasionalmente devolver JSON malformado (retry implementado)
- [ ] Frontend no valida tamaño de archivo antes de upload

### Roadmap
- Q1 2026: MVP1 (completado)
- Q2 2026: MVP2 (múltiples rúbricas, historial)
- Q3 2026: MVP3 (colaboración, integraciones)
- Q4 2026: v2.0 (refactor, performance, escalabilidad)
