
# Mi Web Service (FastAPI + SQLAlchemy + PostgreSQL)

Servicio REST listo para Render: endpoints de productos y usuarios persistentes en PostgreSQL.

## Ejecutar localmente
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Por defecto usa SQLite (demo.db)
python -m app.main
# Docs: http://localhost:8000/api/docs
```

## Variables de entorno
- ENV=production|development
- API_TITLE=Mi Web Service
- ALLOWED_ORIGINS=*
- DATABASE_URL=postgresql://user:pass@host:5432/dbname  (Render la inyecta automáticamente con el blueprint)

## Endpoints
- GET /api/health
- GET /api/time
- CRUD /api/productos
- GET/POST /api/usuarios
- Docs: /api/docs

## Semillas (SQL opcional)
PostgreSQL/MySQL/Oracle comparten el mismo diseño lógico. Para Postgres:
```sql
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario SERIAL PRIMARY KEY,
  nombre     VARCHAR(100) NOT NULL,
  correo     VARCHAR(150) UNIQUE NOT NULL,
  password   VARCHAR(100) NOT NULL,
  fecha_reg  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO usuarios (nombre, correo, password) VALUES
  ('Carlos Obregón','carlos@correo.com','pass123')
  ON CONFLICT DO NOTHING;
```

## Despliegue en Render (Blueprint)
1) Sube este repo a GitHub.
2) En Render: New → Blueprint → selecciona tu repo.
3) Render creará el servicio web y una base de datos Postgres gratis, exponiendo `DATABASE_URL` a la app.
4) Prueba la URL pública: `/api/health`, `/api/docs`.
