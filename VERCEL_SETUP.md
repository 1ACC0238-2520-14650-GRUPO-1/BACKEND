# 🚀 GUÍA RÁPIDA DE DESPLIEGUE EN VERCEL

## ✅ Preparación completada (VERSIÓN 2 - CORREGIDA)

He arreglado el problema de importaciones. Ahora el proyecto debe funcionar en Vercel.

**Cambios realizados:**
- ✅ `api/index.py` - Ahora configura correctamente el path de Python
- ✅ `vercel.json` - Especifica Python 3.12
- ✅ `.gitignore` - Para no subir archivos innecesarios

## 📝 Pasos para desplegar:

### 1️⃣ Preparar base de datos remota
Vercel usa funciones serverless que **no pueden ejecutar migraciones automáticas** como tu app local.

**Opciones recomendadas:**
- **Supabase** (PostgreSQL gratuito): https://supabase.com
- **Railway** (PostgreSQL + otras): https://railway.app
- **AWS RDS** (más caro pero robusto)

Elige una y obtén el `DATABASE_URL`.

### 2️⃣ Conectar repositorio a Vercel
- Ve a https://vercel.com
- Click en "New Project"
- Conecta tu repositorio de GitHub
- Vercel detectará automáticamente que es un proyecto Python

### 3️⃣ Configurar variables de entorno

En Vercel, ve a: `Settings` → `Environment Variables`

Añade **exactamente** estas variables:
```
DATABASE_URL
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
CORS_ORIGINS
ENVIRONMENT
```

Con sus valores correspondientes.

### 4️⃣ Deploy
Click en "Deploy" - Vercel hará el deploy automáticamente.

### 5️⃣ Verificar deploy

Después del deploy:
- URL API: `https://tu-proyecto.vercel.app`
- Docs: `https://tu-proyecto.vercel.app/docs`
- Redoc: `https://tu-proyecto.vercel.app/redoc`

## ⚠️ Limitaciones importantes

- **Máximo 10 segundos de ejecución** por request (plan free)
- **Sin conexiones persistentes** a BD
- **Cada request es un nuevo proceso**

## 🔧 Si sigue fallando

1. Ve a Vercel dashboard → Deployments
2. Abre el último deployment → Logs
3. Busca el error en los logs
4. Los errores comunes son:
   - Variables de entorno mal configuradas
   - Base de datos no accesible
   - Problemas con psycopg2

## 📚 Documentación útil

- Vercel Python: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- FastAPI en Vercel: https://vercel.com/guides/deploying-fastapi-with-vercel

