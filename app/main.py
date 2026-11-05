from datetime import date
from fastapi import Depends, FastAPI, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import services, schemas
from .database import Base, engine, get_db
from .models import TestDrive, Sesion

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Concesionaria IA")


@app.exception_handler(services.ErrorNegocio)
def manejar_error_negocio(request, exc: services.ErrorNegocio):
    return JSONResponse(status_code=exc.status, content={"detail": exc.mensaje})


@app.get("/autos", response_model=list[schemas.AutoOut])
def listar_autos(
    tipo: str | None = None,
    marca: str | None = None,
    combustible: str | None = None,
    precio_min: float | None = None,
    precio_max: float | None = None,
    solo_con_stock: bool = True,
    db: Session = Depends(get_db),
):
    return services.buscar_autos(
        db, tipo, marca, combustible, precio_min, precio_max, solo_con_stock
    )


@app.get("/autos/{auto_id}", response_model=schemas.AutoOut)
def detalle_auto(auto_id: int, db: Session = Depends(get_db)):
    return services.obtener_auto(db, auto_id)


@app.get("/autos/{auto_id}/horarios")
def horarios(auto_id: int, fecha: date = Query(...), db: Session = Depends(get_db)):
    return {
        "auto_id": auto_id,
        "fecha": fecha,
        "horarios_libres": services.horarios_disponibles(db, auto_id, fecha),
    }


@app.post("/test-drives", response_model=schemas.TestDriveOut, status_code=201)
def crear_turno(datos: schemas.TestDriveIn, db: Session = Depends(get_db)):
    return services.agendar_test_drive(
        db, datos.auto_id, datos.nombre_cliente, datos.telefono, datos.fecha_hora
    )


@app.get("/test-drives", response_model=list[schemas.TestDriveOut])
def listar_turnos(db: Session = Depends(get_db)):
    return db.query(TestDrive).order_by(TestDrive.fecha_hora).all()


# ---------- Chat con Claude ----------
from pydantic import BaseModel
from . import agent
import json


class ChatIn(BaseModel):
    session_id: str
    mensaje: str


@app.post("/chat")
def chat(datos: ChatIn, db: Session = Depends(get_db)):
    fila = db.get(Sesion, datos.session_id)
    historial = json.loads(fila.historial) if fila else []
    historial.append({"role": "user", "content": datos.mensaje})

    respuesta = agent.responder(db, historial)

    texto = json.dumps(historial, ensure_ascii=False)
    if fila:
        fila.historial = texto
    else:
        db.add(Sesion(session_id=datos.session_id, historial=texto))
    db.commit()
    return {"respuesta": respuesta}


# ---------- Frontend ----------
from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
