
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4
from datetime import datetime, timezone
import os

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Usuario, Producto

# ===== Config =====
API_TITLE = os.getenv("API_TITLE", "Mi Web Service")
ENV = os.getenv("ENV", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
origins = ["*"] if ALLOWED_ORIGINS.strip() == "*" else [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=API_TITLE,
    version="1.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Helpers =====
def ok(message: str, data=None):
    return {"success": True, "message": message, "data": data}

def fail(message: str, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail={"success": False, "message": message})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== Schemas =====
class ProductoIn(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., ge=0)
    stock: int = Field(0, ge=0)

class ProductoOut(ProductoIn):
    id: str

class UsuarioIn(BaseModel):
    nombre: str
    correo: str
    password: str

class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    fecha_reg: datetime | None = None
    class Config:
        orm_mode = True

# ===== Meta =====
@app.get("/", tags=["meta"])
def root():
    return ok("Servicio activo", {
        "env": ENV,
        "docs": "/api/docs",
        "endpoints": [
            "/api/health",
            "/api/time",
            "/api/productos",
            "/api/usuarios"
        ],
    })

@app.get("/api/health", tags=["meta"])
def health():
    return ok("ok")

@app.get("/api/time", tags=["meta"])
def time_now():
    now_utc = datetime.now(timezone.utc).isoformat()
    return ok("Hora del servidor (UTC)", {"utc": now_utc})

# ===== Productos (DB usando SQLAlchemy) =====
@app.get("/api/productos", response_model=List[ProductoOut], tags=["productos"])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    # convertir a dicts
    return [{"id": p.id, "nombre": p.nombre, "precio": p.precio, "stock": p.stock} for p in productos]

@app.post("/api/productos", response_model=ProductoOut, status_code=201, tags=["productos"])
def crear_producto(body: ProductoIn, db: Session = Depends(get_db)):
    pid = str(uuid4())
    p = Producto(id=pid, nombre=body.nombre, precio=body.precio, stock=body.stock)
    db.add(p)
    db.commit()
    return {"id": pid, **body.model_dump()}

@app.get("/api/productos/{pid}", response_model=ProductoOut, tags=["productos"])
def obtener_producto(pid: str, db: Session = Depends(get_db)):
    p = db.get(Producto, pid)
    if not p:
        fail("Producto no encontrado", 404)
    return {"id": p.id, "nombre": p.nombre, "precio": p.precio, "stock": p.stock}

@app.put("/api/productos/{pid}", response_model=ProductoOut, tags=["productos"])
def actualizar_producto(pid: str, body: ProductoIn, db: Session = Depends(get_db)):
    p = db.get(Producto, pid)
    if not p:
        fail("Producto no encontrado", 404)
    p.nombre = body.nombre
    p.precio = body.precio
    p.stock  = body.stock
    db.commit()
    return {"id": p.id, **body.model_dump()}

@app.delete("/api/productos/{pid}", tags=["productos"])
def eliminar_producto(pid: str, db: Session = Depends(get_db)):
    p = db.get(Producto, pid)
    if not p:
        fail("Producto no encontrado", 404)
    db.delete(p)
    db.commit()
    return ok("Eliminado")

# ===== Usuarios =====
@app.get("/api/usuarios", response_model=list[UsuarioOut], tags=["usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@app.post("/api/usuarios", response_model=UsuarioOut, status_code=201, tags=["usuarios"])
def crear_usuario(body: UsuarioIn, db: Session = Depends(get_db)):
    # Nota: en producción hashea password (bcrypt/argon2). Aquí es demo.
    u = Usuario(nombre=body.nombre, correo=body.correo, password=body.password)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

# ===== Ejecutar localmente =====
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=(ENV != "production"))
