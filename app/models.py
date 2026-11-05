from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Auto(Base):
    __tablename__ = "autos"

    id: Mapped[int] = mapped_column(primary_key=True)
    marca: Mapped[str] = mapped_column(String(50))
    modelo: Mapped[str] = mapped_column(String(50))
    anio: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[str] = mapped_column(String(20))  # SUV, Sedan, Hatchback, Pickup
    precio_usd: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str] = mapped_column(String(30))
    combustible: Mapped[str] = mapped_column(String(20))  # Nafta, Diesel, Híbrido, Eléctrico

    turnos: Mapped[list["TestDrive"]] = relationship(back_populates="auto")


class TestDrive(Base):
    __tablename__ = "test_drives"

    id: Mapped[int] = mapped_column(primary_key=True)
    auto_id: Mapped[int] = mapped_column(ForeignKey("autos.id"))
    nombre_cliente: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[str] = mapped_column(String(30))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20), default="confirmado")

    auto: Mapped["Auto"] = relationship(back_populates="turnos")


from sqlalchemy import Text


class Sesion(Base):
    __tablename__ = "sesiones"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    historial: Mapped[str] = mapped_column(Text, default="[]")
