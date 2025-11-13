# Despliegue en Vercel

## Pasos para desplegar en Vercel

### 1. Instalar Vercel CLI
```bash
npm i -g vercel
```

### 2. Configurar variables de entorno en Vercel

Ve al dashboard de Vercel y en tu proyecto añade:
- `DATABASE_URL`: Tu URL de PostgreSQL (ej: conexión remota en Railway, Supabase, etc.)
- `SECRET_KEY`: Una clave secreta fuerte
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `CORS_ORIGINS`: JSON list de orígenes permitidos
- `ENVIRONMENT`: `production`

### 3. Desplegar desde la terminal

**Primera vez (link del repositorio):**
```bash
vercel --prod
```

**Subsecuentes (desde Git):**
El deployment es automático cuando haces push a `main` o puedes ejecutar:
```bash
vercel --prod
```

### 4. Verificar el despliegue

Una vez desplegado, accede a:
- API: `https://tu-proyecto.vercel.app/api/perfil`
- Docs: `https://tu-proyecto.vercel.app/docs`

## Notas importantes

- **Base de datos**: Debes usar una base de datos remota (ej: Supabase, Railway, AWS RDS)
- **Las funciones serverless de Vercel tienen límites**: 
  - Máximo 15 minutos de ejecución
  - No mantienen conexiones persistentes
- **Para desarrollo local**: Usa `uvicorn app.main:app --reload`

## Troubleshooting

Si los tests fallan después del deploy:
1. Verifica que las variables de entorno estén configuradas
2. Comprueba que la BD remota es accesible
3. Revisa los logs en el dashboard de Vercel
