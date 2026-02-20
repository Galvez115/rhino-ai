# Rhino AI - MVP1.1 Hotfix/Iteración

## 🎯 Objetivo

Mejorar la detección de tipo de documento para hacerla 100% equivalente a la IA de Gobierno, implementando un detector determinístico basado en el JSON `document_type_detection_rhino`.

## 📋 Cambios Implementados

### 1. Archivos Nuevos

#### `backend/config/document_type_detection_rhino.json`
- **Descripción**: Configuración completa del detector determinístico
- **Contenido**:
  - Umbrales por tipo de documento (type_thresholds)
  - Pesos de señales (signal_weights)
  - Indicadores fuertes por tipo (strong_indicators)
  - Patrones estructurales (structural_patterns)
  - Reglas de dominancia estructural (dominancia_estructural)
  - Resolución de conflictos (conflict_resolution)
  - Política nombre vs contenido (filename_vs_content_policy)
  - Manejo de UNKNOWN (unknown_handling)

#### `backend/services/doc_type_detector.py`
- **Descripción**: Módulo de detección determinística
- **Funciones principales**:
  - `extract_features()`: Extrae características del documento
  - `has_at_least_one_strong_indicator()`: Verifica indicadores fuertes
  - `check_structural_patterns()`: Detecta patrones estructurales
  - `score_each_type()`: Calcula score 0-100 por tipo
  - `apply_dominancia_estructural()`: Aplica reglas de dominancia
  - `resolve_conflict()`: Resuelve conflictos típicos
  - `select_type()`: Selecciona tipo final con todas las reglas
  - `detect_document_type()`: Entry point principal

#### `backend/tests/test_doc_type_detector.py`
- **Descripción**: Tests unitarios para el detector
- **Tests incluidos**:
  - DTM vs PLAN_PRUEBAS con matriz trazabilidad
  - PLAN_PRUEBAS con pasos/datos/resultados
  - DSP vs DTC con APIs/endpoints
  - DSP con escenarios de negocio
  - RUNBOOK vs DTC con ventanas/monitoreo
  - RCA vs RUNBOOK con timeline/causa raíz
  - Conflicto nombre vs contenido
  - UNKNOWN sin umbral o sin indicadores
  - Top 3 candidatos
  - Indicadores fuertes
  - Patrones estructurales

### 2. Archivos Modificados

#### `backend/api/routes.py`
**Cambios**:
- Reemplazado `classify_document()` por `detect_document_type()`
- Agregado `detection_result_json` al modelo Run
- Pasado `detection_result` al evaluator
- Incluido `detection_result` en respuesta del endpoint

**Líneas modificadas**:
```python
# Antes
from services.classifier import classify_document
doc_type, confidence = await classify_document(outline, run_id)

# Después
from services.doc_type_detector import detect_document_type
detection_result = detect_document_type(filename, headings, tables, full_text)
doc_type = detection_result["tipo_detectado"]
confidence = detection_result["confianza"]
```

#### `backend/services/evaluator.py`
**Cambios**:
- Agregado parámetro `detection_result` al constructor
- Generación de hallazgo MAYOR para conflicto nombre vs contenido
- Impacto estimado: 5.0 puntos

**Nuevo hallazgo**:
```python
if self.detection_result and self.detection_result.get("conflict_name_vs_content"):
    conflict_hallazgo = Hallazgo(
        criterio_id="CONTROL_DOCUMENTAL",
        severidad="mayor",
        prioridad="P1",
        titulo="Conflicto: Nombre de archivo vs Contenido",
        ...
    )
```

#### `backend/storage/database.py`
**Cambios**:
- Agregado campo `detection_result_json` al modelo Run

```python
class Run(Base):
    ...
    detection_result_json = Column(JSON)  # MVP1.1
```

#### `frontend/src/App.jsx`
**Cambios**:
- Agregado estado `detectionResult`
- Guardado de `detection_result` del backend
- Pasado `detectionResult` a ReportStep

#### `frontend/src/components/ReportStep.jsx`
**Cambios**:
- Agregada prop `detectionResult`
- Visualización de confianza en header
- Nueva sección "Detección de Tipo de Documento" con:
  - Tipo detectado, confianza, razón
  - Top 3 candidatos con scores
  - Banner de conflicto nombre vs contenido (si aplica)
  - Preguntas para clasificar (si UNKNOWN)
  - Señales secundarias

## 🔍 Reglas Implementadas

### Scoring (0-100)
- **Filename exact match**: +20 puntos
- **Strong indicator heading**: +15 puntos (máx 3)
- **Strong indicator table**: +12 puntos (máx 2)
- **Keyword density high**: +10 puntos (≥5 keywords)
- **Keyword density medium**: +5 puntos (2-4 keywords)
- **Structural pattern**: +8 puntos (máx 3)

### Candidatos Válidos
Un tipo es candidato SOLO si:
1. `score >= threshold` (umbrales: DTM=60, DSP=55, DTC=60, etc.)
2. `has_at_least_one_strong_indicator = true`

### Desempate
1. **Dominancia estructural**: Si aplica regla if/then
2. **Conflictos típicos**: Aplicar regla específica
3. **Filename**: Si nombre contiene token y contenido no contradice
4. **Score más alto**: Gana el de mayor score

### Conflicto Nombre vs Contenido
Se activa si:
- Nombre sugiere tipo X
- Contenido gana con tipo Y
- Diferencia > 15 puntos
- Contenido tiene ≥ 2 indicadores fuertes

**Resultado**:
- Gana contenido
- `conflict_name_vs_content = true`
- Genera hallazgo MAYOR "Control documental"

### UNKNOWN
Se asigna si:
- Ningún tipo supera umbral, O
- Ningún tipo tiene indicadores fuertes

**Resultado**:
- Devuelve top 3 candidatos
- Incluye `questions_to_classify` (7 preguntas)

## 🧪 Verificación Manual

### Test 1: Documento con nombre DTC pero contenido DTM
```bash
# Crear documento: "configuracion_DTC_v1.docx"
# Contenido: Plan de Migración, Rollback, Inventario de Datos
# Resultado esperado:
# - tipo_detectado: DTM
# - conflict_name_vs_content: true
# - filename_suggested_type: DTC
# - Hallazgo MAYOR de control documental
```

### Test 2: Documento con matrices RF/TC
```bash
# Crear documento: "plan_migracion.docx"
# Contenido: Matriz RF↔TC↔Release, Rollback
# Resultado esperado:
# - tipo_detectado: DTM
# - top3[0].type: DTM
# - Razón: "Dominancia estructural: Matriz RF↔TC↔release"
```

### Test 3: Runbook con rollback operativo
```bash
# Crear documento: "runbook_produccion.docx"
# Contenido: Ventanas de mantenimiento, Monitoreo, Rollback operativo
# Resultado esperado:
# - tipo_detectado: RUNBOOK_MANUAL_OPERACION
# - top3[0].score > 60
```

### Test 4: Documento UNKNOWN
```bash
# Crear documento: "notas_reunion.docx"
# Contenido: Notas genéricas sin keywords específicos
# Resultado esperado:
# - tipo_detectado: UNKNOWN
# - confianza: 0.0
# - questions_to_classify: 7 preguntas
```

## 📊 Compatibilidad

### ✅ Mantiene Compatibilidad
- Scoring de rúbrica (sin cambios)
- Fail-fast (sin cambios)
- Evaluación de criterios (sin cambios)
- Generación de hallazgos (agregado conflicto)
- UI wizard (agregada sección detección)
- Export JSON/MD (incluye detection_result)

### ⚠️ Cambios en Base de Datos
- Agregado campo `detection_result_json` a tabla `runs`
- **Migración**: Automática con SQLAlchemy (create_all)
- **Datos existentes**: Campo será NULL (compatible)

## 🚀 Despliegue

### Pasos
1. Pull cambios del repositorio
2. Reiniciar containers:
   ```bash
   docker-compose down
   docker-compose up --build
   ```
3. La base de datos se actualizará automáticamente

### Verificación
```bash
# 1. Verificar que el detector carga
docker-compose logs backend | grep "doc_type_detector"

# 2. Subir documento de prueba
curl -X POST http://localhost:8000/api/runs \
  -F "file=@test_document.docx"

# 3. Verificar detection_result en respuesta
# Debe incluir: tipo_detectado, confianza, razon, top3, conflict_name_vs_content
```

## 📝 Tests

### Ejecutar Tests
```bash
cd backend
pytest tests/test_doc_type_detector.py -v
```

### Tests Esperados
```
test_dtm_vs_plan_pruebas_with_matriz_trazabilidad PASSED
test_plan_pruebas_with_pasos_datos_resultados PASSED
test_dsp_vs_dtc_with_apis_endpoints PASSED
test_dsp_with_escenarios_negocio PASSED
test_runbook_vs_dtc_with_ventanas_monitoreo PASSED
test_rca_vs_runbook_with_timeline_causa_raiz PASSED
test_conflict_name_vs_content PASSED
test_unknown_without_threshold PASSED
test_unknown_without_strong_indicators PASSED
test_top3_candidates PASSED
test_has_at_least_one_strong_indicator PASSED
test_structural_patterns PASSED
```

## 🎯 Resultado Final

### Antes (MVP1)
- Clasificación: Heurística simple + LLM
- Confianza: Estimada
- Sin top 3 candidatos
- Sin detección de conflictos
- LLM usado siempre

### Después (MVP1.1)
- Clasificación: Determinística con reglas exactas
- Confianza: Calculada con evidencia
- Top 3 candidatos con scores
- Detección de conflicto nombre vs contenido
- LLM solo para empates ±5 puntos
- Hallazgo MAYOR si conflicto
- Preguntas para UNKNOWN

## ✅ Checklist de Verificación

- [x] `document_type_detection_rhino.json` creado
- [x] `doc_type_detector.py` implementado
- [x] Tests unitarios creados y pasando
- [x] `routes.py` actualizado
- [x] `evaluator.py` actualizado
- [x] `database.py` actualizado
- [x] `App.jsx` actualizado
- [x] `ReportStep.jsx` actualizado
- [x] Hallazgo de conflicto implementado
- [x] Top 3 candidatos en UI
- [x] Banner de conflicto en UI
- [x] Preguntas UNKNOWN en UI
- [x] Compatibilidad mantenida
- [x] Documentación actualizada

## 🎉 MVP1.1 Completado

Todos los cambios solicitados han sido implementados y verificados. El sistema ahora usa detección determinística 100% equivalente a la IA de Gobierno.
