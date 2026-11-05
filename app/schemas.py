from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marca: str
    modelo: str
    anio: int
    tipo: str
    precio_usd: float
    stock: int
    color: str
    combustible: str


class TestDriveIn(BaseModel):
    auto_id: int
    nombre_cliente: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=6, max_length=30)
    fecha_hora: datetime


class TestDriveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auto_id: int
    nombre_cliente: str
    telefono: str
    fecha_hora: datetime
    estado: str
