
from sqlalchemy import Column, Integer, String, DateTime, Float, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(100), nullable=False)
    correo     = Column(String(150), unique=True, nullable=False)
    password   = Column(String(100), nullable=False)
    fecha_reg  = Column(DateTime, server_default=func.now())

class Producto(Base):
    __tablename__ = "productos"
    id    = Column(String(36), primary_key=True)  # uuid en texto para simplicidad
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False, default=0)
    stock  = Column(Integer, nullable=False, default=0)
