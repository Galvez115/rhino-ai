# Rhino AI - Checklist Pre-Deploy

## ✅ Verificación Antes de Desplegar

### 1. Requisitos del Sistema

- [ ] Docker Desktop instalado y corriendo
- [ ] Docker version >= 20.0
- [ ] Docker Compose version >= 2.0
- [ ] Puertos 3000 y 8000 disponibles
- [ ] Al menos 2GB RAM disponible
- [ ] Al menos 5GB espacio en disco

**Verificar:**
```bash
docker --version
docker-compose --version
```

### 2. Configuración

- [ ] Archivo `.env` existe (copiado de `sample.env`)
- [ ] `LLM_PROVIDER` configurado (openai o anthropic)
- [ ] API key válida configurada
- [ ] `CORS_ORIGINS` incluye tu dominio (si aplica)
- [ ] `DATABASE_TYPE` configurado (sqlite o postgres)

**Verificar:**
```bash
cat .env | grep API_KEY
# Debe mostrar tu API key (no "your-key-here")
```

### 3. Archivos Críticos

- [ ] `rubrica_government.json` existe en raíz
- [ ] `rubrica_government.json` copiado a `backend/config/`
- [ ] `docker-compose.yml` sin modificaciones no deseadas
- [ ] `backend/requirements.txt` completo
- [ ] `frontend/package.json` completo

**Verificar:**
```bash
ls -la rubrica_government.json
ls -la backend/config/rubrica_government.json
```

### 4. Validación Automática

- [ ] Ejecutar `python validate-setup.py`
- [ ] Todos los checks pasan (✅)
- [ ] No hay errores críticos (❌)

**Ejecutar:**
```bash
python validate-setup.py
```

### 5. Tests

- [ ] Tests unitarios pasan
- [ ] No hay errores de sintaxis
- [ ] No hay imports faltantes

**Ejecutar:**
```bash
cd backend
pytest tests/ -v
```

### 6. Build Docker

- [ ] Backend build exitoso
- [ ] Frontend build exitoso
- [ ] No hay errores en logs

**Ejecutar:**
```bash
docker-compose build
```

### 7. Inicio de Servicios

- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] Database se crea correctamente
- [ ] Logs no muestran errores críticos

**Ejecutar:**
```bash
docker-compose up
# Verificar logs en otra terminal:
docker-compose logs -f
```

### 8. Verificación de Endpoints

- [ ] Frontend accesible en http://localhost:3000
- [ ] Backend accesible en http://localhost:8000
- [ ] API docs accesible en http://localhost:8000/docs
- [ ] Health check responde: http://localhost:8000/health

**Verificar:**
```bash
curl http://localhost:8000/health
# Debe retornar: {"status":"healthy"}
```

### 9. Funcionalidad Básica

- [ ] Upload de archivo DOCX funciona
- [ ] Clasificación de documento funciona
- [ ] Evaluación genera score
- [ ] Preguntas se generan (si aplica)
- [ ] Reporte se muestra correctamente
- [ ] Export JSON funciona
- [ ] Export Markdown funciona

**Test Manual:**
1. Subir documento de prueba
2. Verificar que se procesa
3. Ver reporte generado
4. Descargar exports

### 10. Seguridad

- [ ] `.env` NO está en Git (verificar `.gitignore`)
- [ ] API keys NO están en logs
- [ ] CORS configurado correctamente
- [ ] File upload valida tipo de archivo
- [ ] No hay secrets hardcodeados en código

**Verificar:**
```bash
git status
# .env NO debe aparecer en "Changes to be committed"
```

### 11. Performance

- [ ] Upload de archivo < 5MB toma < 30s
- [ ] Evaluación completa toma < 60s
- [ ] UI responde rápidamente
- [ ] No hay memory leaks visibles

**Monitorear:**
```bash
docker stats
# Verificar uso de CPU y memoria
```

### 12. Logs

- [ ] Logs estructurados en JSON
- [ ] run_id presente en logs
- [ ] Nivel de log apropiado (INFO en prod)
- [ ] No hay stack traces innecesarios

**Verificar:**
```bash
docker-compose logs backend | head -20
# Debe mostrar logs JSON estructurados
```

### 13. Networking (Si compartir con equipo)

- [ ] Firewall permite puertos 3000 y 8000
- [ ] IP local obtenida correctamente
- [ ] Otros pueden acceder desde LAN
- [ ] Tailscale configurado (si aplica)

**Verificar:**
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

### 14. Documentación

- [ ] README.md actualizado
- [ ] ARCHITECTURE.md revisado
- [ ] EXAMPLES.md con casos de uso
- [ ] CHANGELOG.md actualizado
- [ ] Comentarios en código crítico

### 15. Backup

- [ ] Base de datos respaldada (si tiene datos)
- [ ] Configuración respaldada
- [ ] Código en Git (commit reciente)

**Ejecutar:**
```bash
git status
git log -1
```

## 🚨 Errores Comunes y Soluciones

### Error: "Cannot connect to Docker daemon"
**Solución:** Iniciar Docker Desktop

### Error: "Port already in use"
**Solución:** 
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :3000
kill -9 [PID]
```

### Error: "API key invalid"
**Solución:** Verificar `.env` y reiniciar containers

### Error: "Module not found"
**Solución:** Rebuild containers
```bash
docker-compose down
docker-compose up --build
```

## ✅ Checklist Final

Antes de declarar "LISTO PARA PRODUCCIÓN":

- [ ] Todos los items arriba marcados ✅
- [ ] Al menos 1 documento de prueba procesado exitosamente
- [ ] Equipo puede acceder (si compartido)
- [ ] Documentación entregada
- [ ] Backup realizado
- [ ] Plan de rollback definido

## 🎯 Criterios de Aceptación

### Mínimo Viable (MVP1)
- [x] Upload DOCX funciona
- [x] Clasificación automática funciona
- [x] Evaluación con rúbrica funciona
- [x] Hallazgos se generan correctamente
- [x] Preguntas inteligentes funcionan
- [x] Score potencial se calcula
- [x] Export JSON/MD funciona
- [x] UI wizard completo
- [x] Docker Compose funciona

### Deseable
- [ ] Tests E2E implementados
- [ ] Monitoring configurado
- [ ] Alertas configuradas
- [ ] Backup automático
- [ ] CI/CD pipeline

### Futuro (MVP2+)
- [ ] Múltiples rúbricas
- [ ] Historial de evaluaciones
- [ ] Dashboard de métricas
- [ ] API pública con auth

## 📊 Métricas de Éxito

- **Uptime**: > 99% (local)
- **Tiempo de respuesta**: < 60s por evaluación
- **Tasa de error**: < 1%
- **Satisfacción usuario**: Feedback positivo

## 🚀 Deploy

Una vez todos los checks pasen:

```bash
# 1. Commit final
git add .
git commit -m "Ready for deploy - MVP1 complete"

# 2. Tag version
git tag -a v1.0.0 -m "MVP1 Release"

# 3. Deploy
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/health

# 5. Monitorear
docker-compose logs -f
```

## 🎉 ¡Listo!

Si todos los checks pasan:
- ✅ Rhino AI está listo para usar
- ✅ Documentación completa
- ✅ Tests pasan
- ✅ Funcionalidad verificada

**¡Adelante con el deploy!** 🦏🚀
