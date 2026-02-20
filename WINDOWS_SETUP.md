# Rhino AI - Guía de Instalación para Windows

## Requisitos Previos

### 1. Instalar Docker Desktop para Windows

1. Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop/
2. Ejecuta el instalador
3. Reinicia tu computadora si es necesario
4. Abre Docker Desktop y espera a que inicie completamente
5. Verifica la instalación:
   ```cmd
   docker --version
   docker-compose --version
   ```

### 2. Instalar Python (Opcional, para desarrollo)

1. Descarga Python 3.11+ desde: https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Verifica:
   ```cmd
   python --version
   ```

### 3. Instalar Node.js (Opcional, para desarrollo)

1. Descarga Node.js 20+ desde: https://nodejs.org/
2. Ejecuta el instalador (usa las opciones por defecto)
3. Verifica:
   ```cmd
   node --version
   npm --version
   ```

## Instalación Rápida

### Opción 1: Usando el Script Automático

1. Abre PowerShell o CMD en la carpeta del proyecto
2. Ejecuta:
   ```cmd
   quick-start.bat
   ```
3. Sigue las instrucciones en pantalla

### Opción 2: Manual

1. **Copiar configuración**
   ```cmd
   copy sample.env .env
   ```

2. **Editar .env**
   - Abre `.env` con Notepad o tu editor favorito
   - Agrega tu API key:
     ```
     LLM_PROVIDER=openai
     OPENAI_API_KEY=sk-tu-key-aqui
     ```

3. **Iniciar con Docker**
   ```cmd
   docker-compose up --build
   ```

4. **Acceder a la aplicación**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Desarrollo Local (Sin Docker)

### Backend

1. **Crear entorno virtual**
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Instalar dependencias**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Ejecutar**
   ```cmd
   uvicorn main:app --reload --port 8000
   ```

### Frontend

1. **Instalar dependencias**
   ```cmd
   cd frontend
   npm install
   ```

2. **Ejecutar**
   ```cmd
   npm run dev
   ```

## Solución de Problemas

### Error: "Docker no está corriendo"

**Solución:**
1. Abre Docker Desktop
2. Espera a que el ícono de Docker en la bandeja del sistema esté verde
3. Intenta de nuevo

### Error: "Puerto 3000 o 8000 ya está en uso"

**Solución:**
1. Encuentra el proceso que usa el puerto:
   ```cmd
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```
2. Mata el proceso:
   ```cmd
   taskkill /PID [número_de_proceso] /F
   ```
3. O cambia el puerto en `docker-compose.yml`

### Error: "No se puede conectar al backend"

**Solución:**
1. Verifica que el backend esté corriendo:
   ```cmd
   docker-compose ps
   ```
2. Revisa los logs:
   ```cmd
   docker-compose logs backend
   ```
3. Verifica que `.env` tenga la API key correcta

### Error: "python-docx no puede leer el archivo"

**Solución:**
1. Asegúrate de que el archivo sea .docx (no .doc)
2. Abre el archivo en Word y guárdalo como .docx
3. Verifica que el archivo no esté corrupto

### Error: "LLM API key inválida"

**Solución:**
1. Verifica que la API key en `.env` sea correcta
2. Para OpenAI: debe empezar con `sk-`
3. Para Anthropic: debe empezar con `sk-ant-`
4. Reinicia los containers:
   ```cmd
   docker-compose down
   docker-compose up --build
   ```

## Firewall de Windows

Para permitir que otros en tu red accedan:

1. Abre "Windows Defender Firewall"
2. Click en "Configuración avanzada"
3. Click en "Reglas de entrada"
4. Click en "Nueva regla..."
5. Selecciona "Puerto" → Siguiente
6. TCP, puertos específicos: `3000, 8000` → Siguiente
7. "Permitir la conexión" → Siguiente
8. Marca todas las redes → Siguiente
9. Nombre: "Rhino AI" → Finalizar

## Obtener tu IP Local

Para compartir con tu equipo:

```cmd
ipconfig
```

Busca "Dirección IPv4" en tu adaptador de red activo (WiFi o Ethernet).

Ejemplo: `192.168.1.100`

Comparte con tu equipo:
- Frontend: `http://192.168.1.100:3000`
- Backend: `http://192.168.1.100:8000`

## Usar con Tailscale (Recomendado)

1. **Instalar Tailscale**
   - Descarga desde: https://tailscale.com/download/windows
   - Ejecuta el instalador
   - Inicia sesión con tu cuenta

2. **Obtener tu IP de Tailscale**
   - Click en el ícono de Tailscale en la bandeja
   - Copia tu IP (ejemplo: `100.x.x.x`)

3. **Compartir con tu equipo**
   - Pide a tus compañeros que instalen Tailscale
   - Comparte: `http://100.x.x.x:3000`

## Comandos Útiles

### Ver logs en tiempo real
```cmd
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Reiniciar servicios
```cmd
docker-compose restart
```

### Detener todo
```cmd
docker-compose down
```

### Limpiar todo (incluyendo volúmenes)
```cmd
docker-compose down -v
```

### Ver containers corriendo
```cmd
docker ps
```

### Ejecutar tests
```cmd
cd backend
pytest tests/ -v
```

## Validar Instalación

Ejecuta el script de validación:

```cmd
python validate-setup.py
```

Debe mostrar:
```
✅ All checks passed (X/X)
🚀 Ready to start!
```

## Atajos de Teclado en PowerShell

- `Ctrl + C`: Detener el servidor
- `↑` / `↓`: Navegar historial de comandos
- `Tab`: Autocompletar

## Editor Recomendado

- **Visual Studio Code**: https://code.visualstudio.com/
  - Extensiones recomendadas:
    - Python
    - Pylance
    - ES7+ React/Redux/React-Native snippets
    - Docker

## Próximos Pasos

1. ✅ Instalar Docker Desktop
2. ✅ Copiar y configurar `.env`
3. ✅ Ejecutar `quick-start.bat`
4. ✅ Abrir http://localhost:3000
5. ✅ Subir un documento DOCX de prueba
6. ✅ Ver el reporte generado

## Soporte

Si tienes problemas:
1. Revisa esta guía
2. Ejecuta `python validate-setup.py`
3. Revisa los logs: `docker-compose logs`
4. Consulta README.md y ARCHITECTURE.md

¡Listo para usar Rhino AI! 🦏
