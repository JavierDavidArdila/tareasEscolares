# 🌟 Sistema de Tareas para Niños

Una aplicación web para gestionar tareas con sistema de recompensas (estrellas y medallas).

## 🚀 Despliegue en Render.com

### Comando de Ejecución:
```bash
python app.py
```

### Pasos para desplegar:

1. **Crear repositorio en GitHub:**
   - Sube todos los archivos de la carpeta `sistema-tareas`
   - Incluye: `app.py`, `requirements.txt`, `README.md`

2. **En Render.com:**
   - Crear nuevo "Web Service"
   - Conectar con tu repositorio de GitHub
   - Configuración:
     - **Build Command:** `# No build required`
     - **Start Command:** `python app.py`
     - **Environment:** Python 3

3. **Variables de entorno:**
   - Render automáticamente provee la variable `PORT`
   - No se requieren variables adicionales

## 📱 Tecnologías Utilizadas:
- **Backend:** Python (solo librerías estándar)
- **Frontend:** HTML5, CSS3, JavaScript Vanilla
- **Base de datos:** JSON file (tasks.json)

## 🎯 Características:
- ✅ CRUD completo de tareas
- 🏆 Sistema de recompensas (estrellas y medallas)
- 📅 Vista de calendario interactiva
- 💬 Comentarios y progreso de tareas
- 📱 Diseño responsive

## 🏃‍♂️ Ejecutar localmente:
```bash
python app.py
```
Acceder a: http://localhost:8001