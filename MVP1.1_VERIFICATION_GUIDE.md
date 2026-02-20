# Guía de Verificación MVP1.1

## 🎯 Objetivo

Verificar que la detección determinística de tipo de documento funciona correctamente según las especificaciones de Gobierno.

## 📋 Pre-requisitos

```bash
# 1. Asegurarse de tener las dependencias instaladas
cd backend
pip install -r requirements.txt

# 2. Verificar que el archivo de configuración existe
ls config/document_type_detection_rhino.json
```

## 🧪 Tests Automatizados

### Ejecutar todos los tests del detector

```bash
cd backend
pytest tests/test_doc_type_detector.py -v
```

### Tests esperados (12 tests)

```
✅ test_dtm_vs_plan_pruebas_with_matriz_trazabilidad
✅ test_plan_pruebas_with_pasos_datos_resultados
✅ test_dsp_vs_dtc_with_apis_endpoints
✅ test_dsp_with_escenarios_negocio
✅ test_runbook_vs_dtc_with_ventanas_monitoreo
✅ test_rca_vs_runbook_with_timeline_causa_raiz
✅ test_conflict_name_vs_content
✅ test_unknown_without_threshold
✅ test_unknown_without_strong_indicators
✅ test_top3_candidates
✅ test_has_at_least_one_strong_indicator
✅ test_structural_patterns
```

## 📝 Verificación Manual

### Test 1: Conflicto Nombre vs Contenido

**Objetivo**: Verificar que se detecta cuando el nombre sugiere un tipo pero el contenido indica otro.

**Pasos**:
1. Crear documento Word: `configuracion_DTC_setup.docx`
2. Agregar contenido de DTM:
   ```
   Plan de Migración de Base de Datos
   
   1. Inventario de Datos
   - Tablas origen: 50
   - Tablas destino: 50
   
   2. Estrategia de Migración
   - Enfoque: Por fases
   - Herramientas: Scripts SQL
   
   3. Plan de Rollback
   - Backup completo pre-migración
   - Scripts de reversión
   - Tiempo estimado: 2 horas
   
   4. Validación Post-Migración
   - Verificar integridad de datos
   - Comparar counts
   ```

3. Subir documento:
   ```bash
   curl -X POST http://localhost:8000/api/runs \
     -F "file=@configuracion_DTC_setup.docx" \
     -o result.json
   ```

4. Verificar resultado:
   ```bash
   cat result.json | jq '.detection_result'
   ```

**Resultado Esperado**:
```json
{
  "tipo_detectado": "DTM",
  "confianza": 0.75,
  "conflict_name_vs_content": true,
  "filename_suggested_type": "DTC",
  "razon": "Score más alto: 75.0 vs 45.0 | CONFLICTO: nombre sugiere DTC pero contenido gana por 30.0 puntos",
  "top3": [
    {"type": "DTM", "score": 75.0, "why": "..."},
    {"type": "DTC", "score": 45.0, "why": "..."},
    {"type": "DSP", "score": 20.0, "why": "..."}
  ]
}
```

**Verificar en UI**:
- Abrir http://localhost:3000
- Subir el documento
- En la sección "Detección de Tipo de Documento":
  - ✅ Debe mostrar banner naranja "⚠️ Conflicto: Nombre vs Contenido"
  - ✅ Debe indicar que nombre sugiere DTC pero contenido indica DTM
- En "Hallazgos":
  - ✅ Debe aparecer hallazgo MAYOR "Conflicto: Nombre de archivo vs Contenido"
  - ✅ Prioridad: P1
  - ✅ Recomendación: Actualizar nombre del archivo

---

### Test 2: DTM con Matriz de Trazabilidad

**Objetivo**: Verificar que la dominancia estructural funciona correctamente.

**Pasos**:
1. Crear documento: `plan_migracion_oracle_postgres.docx`
2. Agregar contenido:
   ```
   Plan de Migración Oracle a PostgreSQL
   
   1. Inventario de Datos
   - Base origen: Oracle 19c
   - Base destino: PostgreSQL 15
   
   2. Matriz de Trazabilidad RF-TC-Release
   
   | RF     | TC      | Release | Estado |
   |--------|---------|---------|--------|
   | RF-001 | TC-001  | 1.0     | OK     |
   | RF-002 | TC-002  | 1.0     | OK     |
   | RF-003 | TC-003  | 1.1     | Pend   |
   
   3. Plan de Rollback
   - Backup completo
   - Scripts de reversión
   - Validación post-rollback
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "DTM",
  "confianza": 0.85,
  "razon": "Dominancia estructural: Matriz RF↔TC↔release es distintiva de DTM",
  "top3": [
    {"type": "DTM", "score": 85.0, "why": "..."},
    {"type": "PLAN_PRUEBAS_EVIDENCIA", "score": 55.0, "why": "..."},
    {"type": "DSP", "score": 30.0, "why": "..."}
  ]
}
```

---

### Test 3: Plan de Pruebas con Pasos/Datos/Resultados

**Objetivo**: Verificar que se distingue correctamente de DTM.

**Pasos**:
1. Crear documento: `plan_pruebas_integracion.docx`
2. Agregar contenido:
   ```
   Plan de Pruebas de Integración
   
   1. Casos de Prueba
   
   TC-001: Validar Login
   Pasos:
   1. Abrir aplicación
   2. Ingresar usuario: test@example.com
   3. Ingresar contraseña: Test123!
   4. Click en "Iniciar Sesión"
   
   Datos de Prueba:
   - Usuario válido: test@example.com
   - Usuario inválido: invalid@example.com
   
   Resultado Esperado:
   - Usuario autenticado correctamente
   - Redirección a dashboard
   
   Resultado Obtenido:
   - ✅ OK - Usuario autenticado
   - ✅ OK - Redirección correcta
   
   Evidencia:
   - Screenshot: login_success.png
   - Log: auth.log línea 145
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "PLAN_PRUEBAS_EVIDENCIA",
  "confianza": 0.80,
  "razon": "Conflict resolution: Si tiene pasos/datos/resultados => PLAN_PRUEBAS",
  "top3": [
    {"type": "PLAN_PRUEBAS_EVIDENCIA", "score": 80.0, "why": "..."},
    {"type": "DTM", "score": 40.0, "why": "..."},
    {"type": "DoD", "score": 25.0, "why": "..."}
  ]
}
```

---

### Test 4: DTC con APIs y Códigos de Error

**Objetivo**: Verificar que se distingue de DSP.

**Pasos**:
1. Crear documento: `configuracion_api_gateway.docx`
2. Agregar contenido:
   ```
   Configuración API Gateway
   
   1. Endpoints
   
   | Método | Endpoint      | Descripción       |
   |--------|---------------|-------------------|
   | GET    | /api/users    | Listar usuarios   |
   | POST   | /api/users    | Crear usuario     |
   | PUT    | /api/users/:id| Actualizar usuario|
   | DELETE | /api/users/:id| Eliminar usuario  |
   
   2. Autenticación
   - Tipo: OAuth2
   - Token: Bearer
   - Expiración: 3600s
   
   3. Códigos de Error
   
   | Código | Descripción           | Acción                |
   |--------|-----------------------|-----------------------|
   | 400    | Bad Request           | Validar parámetros    |
   | 401    | Unauthorized          | Verificar token       |
   | 403    | Forbidden             | Verificar permisos    |
   | 404    | Not Found             | Verificar recurso     |
   | 500    | Internal Server Error | Revisar logs          |
   
   4. Parámetros de Configuración
   - MAX_CONNECTIONS: 1000
   - TIMEOUT: 30s
   - RETRY_ATTEMPTS: 3
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "DTC",
  "confianza": 0.85,
  "razon": "Conflict resolution: Si tiene APIs/endpoints/códigos error => DTC",
  "top3": [
    {"type": "DTC", "score": 85.0, "why": "..."},
    {"type": "DSP", "score": 50.0, "why": "..."},
    {"type": "RUNBOOK_MANUAL_OPERACION", "score": 30.0, "why": "..."}
  ]
}
```

---

### Test 5: Runbook con Ventanas y Monitoreo

**Objetivo**: Verificar que se distingue de DTC.

**Pasos**:
1. Crear documento: `runbook_produccion.docx`
2. Agregar contenido:
   ```
   Runbook de Producción
   
   1. Procedimientos de Inicio y Parada
   
   Inicio:
   1. Verificar servicios dependientes
   2. Ejecutar: systemctl start app
   3. Verificar logs: tail -f /var/log/app.log
   4. Validar health check: curl http://localhost:8080/health
   
   Parada:
   1. Drenar conexiones activas
   2. Ejecutar: systemctl stop app
   3. Verificar procesos: ps aux | grep app
   
   2. Monitoreo y Alertas
   
   Dashboard: Grafana - http://grafana.internal/dashboard/prod
   
   Alertas Críticas:
   - CPU > 80% durante 5 minutos
   - Memoria > 90% durante 3 minutos
   - Disco > 85%
   - Response time > 2s
   
   3. Ventanas de Mantenimiento
   
   | Día      | Horario      | Duración | Tipo        |
   |----------|--------------|----------|-------------|
   | Domingo  | 02:00-04:00  | 2h       | Mantenimiento|
   | Miércoles| 23:00-01:00  | 2h       | Parches     |
   
   4. Rollback Operativo
   
   Si se detecta problema:
   1. Detener servicio
   2. Revertir a versión anterior: ./rollback.sh v1.2.3
   3. Reiniciar servicio
   4. Validar funcionamiento
   5. Notificar a equipo
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "RUNBOOK_MANUAL_OPERACION",
  "confianza": 0.85,
  "razon": "Dominancia estructural: Ventanas + monitoreo son distintivos de Runbook",
  "top3": [
    {"type": "RUNBOOK_MANUAL_OPERACION", "score": 85.0, "why": "..."},
    {"type": "DTC", "score": 45.0, "why": "..."},
    {"type": "DTM", "score": 30.0, "why": "..."}
  ]
}
```

---

### Test 6: RCA con Timeline y Causa Raíz

**Objetivo**: Verificar que se distingue de Runbook.

**Pasos**:
1. Crear documento: `rca_incidente_20260220.docx`
2. Agregar contenido:
   ```
   Root Cause Analysis - Incidente 20/02/2026
   
   1. Resumen Ejecutivo
   
   Incidente: Caída del servicio de autenticación
   Duración: 2 horas 15 minutos
   Impacto: 5,000 usuarios afectados
   Causa raíz: Índice faltante en tabla usuarios
   
   2. Timeline del Incidente
   
   | Hora  | Evento                                    |
   |-------|-------------------------------------------|
   | 14:00 | Inicio del incidente - Timeouts en login |
   | 14:05 | Alerta de Grafana - Response time > 5s    |
   | 14:10 | Equipo notificado                         |
   | 14:15 | Investigación iniciada                    |
   | 14:30 | Causa identificada - Query lenta          |
   | 14:45 | Índice creado en tabla usuarios           |
   | 15:00 | Servicio restaurado                       |
   | 16:15 | Validación completa                       |
   
   3. Análisis de Causa Raíz (5 Whys)
   
   1. ¿Por qué falló el servicio?
      - Timeouts en base de datos
   
   2. ¿Por qué hubo timeouts?
      - Query de autenticación muy lenta (>5s)
   
   3. ¿Por qué la query era lenta?
      - Full table scan en tabla usuarios (500K registros)
   
   4. ¿Por qué full table scan?
      - Falta índice en columna email
   
   5. ¿Por qué faltaba el índice?
      - No se incluyó en script de migración inicial
   
   Causa Raíz: Índice faltante en columna email de tabla usuarios
   
   4. Acciones Preventivas
   
   | Acción                              | Responsable | Fecha Límite | Estado |
   |-------------------------------------|-------------|--------------|--------|
   | Crear índice en email               | DBA         | 20/02/2026   | ✅ Done|
   | Revisar todos los índices           | DBA         | 25/02/2026   | En progreso|
   | Agregar monitoreo de queries lentas | DevOps      | 28/02/2026   | Pendiente|
   | Actualizar runbook con troubleshooting| Tech Lead | 01/03/2026   | Pendiente|
   
   5. Lecciones Aprendidas
   
   - Implementar revisión de índices en code review
   - Agregar alertas proactivas para queries > 1s
   - Mejorar documentación de troubleshooting
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "SOPORTE_EVOLUTIVO_RCA",
  "confianza": 0.90,
  "razon": "Dominancia estructural: Timeline + causa raíz son distintivos de RCA",
  "top3": [
    {"type": "SOPORTE_EVOLUTIVO_RCA", "score": 90.0, "why": "..."},
    {"type": "RUNBOOK_MANUAL_OPERACION", "score": 40.0, "why": "..."},
    {"type": "DTM", "score": 25.0, "why": "..."}
  ]
}
```

---

### Test 7: Documento UNKNOWN

**Objetivo**: Verificar que se detecta correctamente cuando no hay suficiente información.

**Pasos**:
1. Crear documento: `notas_reunion.docx`
2. Agregar contenido:
   ```
   Notas de Reunión - Equipo de Desarrollo
   
   Fecha: 20/02/2026
   Asistentes: Juan, María, Pedro
   
   Temas Discutidos:
   - Revisión del sprint actual
   - Planificación del próximo sprint
   - Discusión sobre arquitectura
   
   Pendientes:
   - Juan: Revisar documentación
   - María: Actualizar diagramas
   - Pedro: Preparar demo
   
   Próxima reunión: 27/02/2026
   ```

3. Subir y verificar

**Resultado Esperado**:
```json
{
  "tipo_detectado": "UNKNOWN",
  "confianza": 0.0,
  "razon": "Ningún tipo supera umbral o tiene indicadores fuertes",
  "top3": [
    {"type": "DoD", "score": 25.0, "why": "..."},
    {"type": "DSP", "score": 20.0, "why": "..."},
    {"type": "DTM", "score": 15.0, "why": "..."}
  ],
  "questions_to_classify": [
    "¿El documento describe un proceso de migración de datos o sistemas?",
    "¿El documento propone una solución técnica o arquitectura?",
    "¿El documento contiene parámetros de configuración y procedimientos de setup?",
    "¿El documento es un checklist de criterios de aceptación (Definition of Done)?",
    "¿El documento contiene casos de prueba con pasos y resultados esperados?",
    "¿El documento describe procedimientos operativos (inicio, parada, monitoreo)?",
    "¿El documento analiza un incidente con timeline y causa raíz?"
  ]
}
```

**Verificar en UI**:
- ✅ Debe mostrar card azul con "❓ Preguntas para Clasificar"
- ✅ Debe listar las 7 preguntas
- ✅ Debe indicar que no se pudo determinar el tipo con confianza

---

## ✅ Checklist de Verificación

### Tests Automatizados
- [ ] Todos los tests pasan (12/12)
- [ ] No hay errores de import
- [ ] No hay warnings críticos

### Verificación Manual
- [ ] Test 1: Conflicto nombre vs contenido ✅
- [ ] Test 2: DTM con matriz trazabilidad ✅
- [ ] Test 3: Plan de pruebas con pasos ✅
- [ ] Test 4: DTC con APIs ✅
- [ ] Test 5: Runbook con ventanas ✅
- [ ] Test 6: RCA con timeline ✅
- [ ] Test 7: Documento UNKNOWN ✅

### UI
- [ ] Top 3 candidatos se muestran correctamente
- [ ] Banner de conflicto aparece cuando corresponde
- [ ] Preguntas UNKNOWN se muestran en card azul
- [ ] Confianza se muestra en header
- [ ] Hallazgo de conflicto aparece en lista

### API
- [ ] Endpoint `/api/runs` retorna `detection_result`
- [ ] `detection_result` incluye todos los campos esperados
- [ ] Re-evaluación mantiene `detection_result`
- [ ] Export JSON incluye `detection_result`

## 🎯 Criterios de Éxito

MVP1.1 está completo si:
1. ✅ Todos los tests automatizados pasan
2. ✅ Los 7 tests manuales funcionan correctamente
3. ✅ UI muestra toda la información de detección
4. ✅ Hallazgo de conflicto se genera cuando corresponde
5. ✅ No hay regresiones en funcionalidad existente

## 📞 Soporte

Si algún test falla:
1. Revisar logs: `docker-compose logs backend`
2. Verificar configuración: `cat backend/config/document_type_detection_rhino.json`
3. Ejecutar test específico: `pytest tests/test_doc_type_detector.py::test_nombre -v`
4. Consultar `MVP1.1_CHANGES.md` para detalles de implementación
