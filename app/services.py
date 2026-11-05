from datetime import date, datetime, time
from sqlalchemy.orm import Session
from .models import Auto, TestDrive

HORA_INICIO = 9   # primer turno 09:00
HORA_FIN = 18     # último turno 17:00 (turnos de 1 hora)


class ErrorNegocio(Exception):
    """Error de regla de negocio. Lleva un status HTTP sugerido."""

    def __init__(self, mensaje: str, status: int = 400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def buscar_autos(
    db: Session,
    tipo: str | None = None,
    marca: str | None = None,
    combustible: str | None = None,
    precio_min: float | None = None,
    precio_max: float | None = None,
    solo_con_stock: bool = True,
) -> list[Auto]:
    q = db.query(Auto)
    if tipo:
        q = q.filter(Auto.tipo.ilike(tipo))
    if marca:
        q = q.filter(Auto.marca.ilike(marca))
    if combustible:
        q = q.filter(Auto.combustible.ilike(combustible))
    if precio_min is not None:
        q = q.filter(Auto.precio_usd >= precio_min)
    if precio_max is not None:
        q = q.filter(Auto.precio_usd <= precio_max)
    if solo_con_stock:
        q = q.filter(Auto.stock > 0)
    return q.order_by(Auto.precio_usd).all()


def obtener_auto(db: Session, auto_id: int) -> Auto:
    auto = db.get(Auto, auto_id)
    if not auto:
        raise ErrorNegocio(f"No existe el auto con id {auto_id}", 404)
    return auto


def horarios_disponibles(db: Session, auto_id: int, fecha: date) -> list[str]:
    obtener_auto(db, auto_id)

    if fecha < date.today():
        raise ErrorNegocio("La fecha ya pasó")
    if fecha.weekday() == 6:
        return []  # domingo cerrado

    ocupados = {
        t.fecha_hora.hour
        for t in db.query(TestDrive).filter(
            TestDrive.auto_id == auto_id,
            TestDrive.estado == "confirmado",
            TestDrive.fecha_hora >= datetime.combine(fecha, time.min),
            TestDrive.fecha_hora <= datetime.combine(fecha, time.max),
        )
    }

    ahora = datetime.now()
    libres = []
    for h in range(HORA_INICIO, HORA_FIN):
        if h in ocupados:
            continue
        if fecha == date.today() and h <= ahora.hour:
            continue
        libres.append(f"{h:02d}:00")
    return libres


def agendar_test_drive(
    db: Session,
    auto_id: int,
    nombre_cliente: str,
    telefono: str,
    fecha_hora: datetime,
) -> TestDrive:
    auto = obtener_auto(db, auto_id)
    if auto.stock <= 0:
        raise ErrorNegocio(f"El {auto.marca} {auto.modelo} no tiene stock para test drive")

    fecha_hora = fecha_hora.replace(minute=0, second=0, microsecond=0)
    libres = horarios_disponibles(db, auto_id, fecha_hora.date())
    if f"{fecha_hora.hour:02d}:00" not in libres:
        raise ErrorNegocio("Ese horario no está disponible", 409)

    turno = TestDrive(
        auto_id=auto_id,
        nombre_cliente=nombre_cliente,
        telefono=telefono,
        fecha_hora=fecha_hora,
        estado="confirmado",
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return turno
