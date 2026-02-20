# 🦏 Bienvenido a Rhino AI

## ¡Gracias por usar Rhino AI!

Este es tu asistente inteligente para pre-check de entregables técnicos.

## 🎯 ¿Qué hace Rhino AI?

Rhino AI analiza tus documentos DOCX y:
- ✅ Identifica el tipo de documento automáticamente
- ✅ Evalúa con rúbrica gubernamental exacta
- ✅ Genera hallazgos priorizados con evidencia
- ✅ Te hace preguntas inteligentes solo sobre lo crítico
- ✅ Calcula score actual y potencial
- ✅ Te guía para mejorar tu documento

**Importante**: Rhino AI NO modifica tu documento, solo analiza y recomienda.

## 🚀 Inicio en 3 Pasos

### 1️⃣ Configurar

**Windows:**
```cmd
quick-start.bat
```

**Linux/Mac:**
```bash
./quick-start.sh
```

O manualmente:
```bash
cp sample.env .env
# Editar .env y agregar tu API key de OpenAI o Anthropic
```

### 2️⃣ Iniciar

```bash
docker-compose up --build
```

### 3️⃣ Usar

1. Abre http://localhost:3000
2. Sube tu documento DOCX
3. Responde las preguntas (opcional)
4. Ve tu reporte con hallazgos y recomendaciones
5. Exporta en JSON o Markdown

## 📚 Documentación

### Para Empezar
- **README.md** - Instalación y uso básico
- **WINDOWS_SETUP.md** - Guía específica para Windows
- **QUICK_REFERENCE.md** - Comandos rápidos

### Para Entender
- **ARCHITECTURE.md** - Diseño técnico detallado
- **EXAMPLES.md** - Casos de uso y ejemplos
- **PROJECT_SUMMARY.md** - Resumen ejecutivo

### Para Desarrollar
- **CONTRIBUTING.md** - Guía de desarrollo
- **CHANGELOG.md** - Historial de versiones

## 🎓 Tipos de Documentos Soportados

- **DTM**: Documento Técnico de Migración
- **DSP**: Documento de Solución Propuesta
- **DTC**: Documento Técnico de Configuración
- **DoD**: Definition of Done
- **PLAN_PRUEBAS_EVIDENCIA**: Plan de Pruebas y Evidencia
- **RUNBOOK_MANUAL_OPERACION**: Runbook o Manual de Operación
- **SOPORTE_EVOLUTIVO_RCA**: Soporte Evolutivo o RCA

## 🔑 Requisitos

### Obligatorios
- Docker Desktop (Windows/Mac) o Docker + Docker Compose (Linux)
- API Key de OpenAI (GPT-4) o Anthropic (Claude)

### Opcionales (solo para desarrollo)
- Python 3.11+
- Node.js 20+

## ⚡ Validar Instalación

```bash
python validate-setup.py
```

Debe mostrar:
```
✅ All checks passed
🚀 Ready to start!
```

## 🌐 Compartir con tu Equipo

### Opción 1: Red Local (LAN)
1. Obtén tu IP: `ipconfig` (Windows) o `ifconfig` (Linux/Mac)
2. Comparte: `http://TU_IP:3000`

### Opción 2: Tailscale (Recomendado)
1. Instala Tailscale: https://tailscale.com/download
2. Comparte tu IP Tailscale: `http://100.x.x.x:3000`

### Opción 3: Cloudflare Tunnel
1. Instala cloudflared
2. Crea túnel público
3. Comparte URL: `https://rhino-ai.tudominio.com`

## 🎨 Ejemplo de Uso

```
1. Subes: "Plan_Migracion_Oracle_PostgreSQL.docx"
   ↓
2. Rhino AI detecta: DTM (Documento Técnico de Migración)
   ↓
3. Evalúa con rúbrica específica de DTM
   ↓
4. Te pregunta sobre gaps críticos:
   - "¿Puede proporcionar el plan de rollback detallado?"
   - "¿Cuáles son los casos de prueba de validación?"
   ↓
5. Respondes (o saltas)
   ↓
6. Recibes reporte con:
   - Score: 72/100
   - Decisión: REQUIERE_CORRECCION
   - 8 hallazgos priorizados
   - Score potencial si corriges: 85/100
   - Recomendaciones detalladas con ejemplos
```

## 🆘 Problemas Comunes

### "Docker no está corriendo"
→ Abre Docker Desktop y espera a que inicie

### "Puerto 3000 ya está en uso"
→ Cierra otras apps o cambia puerto en `docker-compose.yml`

### "API key inválida"
→ Verifica `.env` y reinicia: `docker-compose restart`

### "No se puede leer el archivo"
→ Asegúrate de que sea .docx (no .doc)

## 📞 Soporte

- **Documentación**: Ver archivos .md en la raíz
- **Validación**: `python validate-setup.py`
- **Logs**: `docker-compose logs -f`

## 🎉 ¡Listo para Empezar!

```bash
# 1. Configurar
cp sample.env .env
# Editar .env con tu API key

# 2. Iniciar
docker-compose up --build

# 3. Abrir
http://localhost:3000

# 4. Subir documento y ver magia ✨
```

## 🏆 Características Destacadas

- ✅ **100% Local**: Funciona en tu máquina, gratis
- ✅ **Multi-LLM**: OpenAI o Anthropic, tú eliges
- ✅ **Anti-Alucinación**: Solo afirma con evidencia
- ✅ **Inteligente**: Preguntas solo lo crítico
- ✅ **Guía Detallada**: Qué agregar, dónde, con ejemplos
- ✅ **Score Potencial**: Ve cuánto puedes mejorar
- ✅ **Export**: JSON y Markdown para compartir

## 📈 Próximos Pasos

1. ✅ Lee README.md para instalación completa
2. ✅ Ejecuta `python validate-setup.py`
3. ✅ Inicia con `docker-compose up --build`
4. ✅ Sube tu primer documento
5. ✅ Explora EXAMPLES.md para casos de uso
6. ✅ Lee ARCHITECTURE.md si quieres entender cómo funciona

## 💡 Tips

- Usa documentos con estructura clara (headings)
- Incluye keywords específicos del tipo de documento
- Responde las preguntas de Rhino AI para mejor evaluación
- Exporta el reporte en Markdown para compartir con tu equipo

## 🚀 ¡Adelante!

Rhino AI está listo para ayudarte a mejorar la calidad de tus entregables.

**¡Comienza ahora!** 🦏✨
