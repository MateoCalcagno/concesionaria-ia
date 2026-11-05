import json
from datetime import date, datetime
from sqlalchemy.orm import Session
from . import services

TOOLS = [
    {
        "name": "buscar_autos",
        "description": (
            "Busca autos en el stock de la concesionaria. Todos los filtros son "
            "opcionales y se pueden combinar. Devuelve los autos ordenados por precio."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tipo": {"type": "string", "enum": ["SUV", "Sedan", "Hatchback", "Pickup"]},
                "marca": {"type": "string", "description": "Ej: Toyota, Volkswagen"},
                "combustible": {"type": "string", "enum": ["Nafta", "Diesel", "Híbrido", "Eléctrico"]},
                "precio_min": {"type": "number", "description": "Precio mínimo en USD"},
                "precio_max": {"type": "number", "description": "Precio máximo en USD"},
            },
        },
    },
    {
        "name": "ver_horarios",
        "description": "Devuelve los horarios libres de test drive de un auto en una fecha.",
        "input_schema": {
            "type": "object",
            "properties": {
                "auto_id": {"type": "integer"},
                "fecha": {"type": "string", "description": "Formato YYYY-MM-DD"},
            },
            "required": ["auto_id", "fecha"],
        },
    },
    {
        "name": "agendar_test_drive",
        "description": (
            "Agenda un test drive. Usar SOLO cuando el cliente ya confirmó auto, "
            "fecha, hora, nombre y teléfono."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "auto_id": {"type": "integer"},
                "nombre_cliente": {"type": "string"},
                "telefono": {"type": "string"},
                "fecha_hora": {"type": "string", "description": "Formato YYYY-MM-DDTHH:00:00"},
            },
            "required": ["auto_id", "nombre_cliente", "telefono", "fecha_hora"],
        },
    },
]


def _auto_a_dict(a):
    return {
        "id": a.id, "marca": a.marca, "modelo": a.modelo, "anio": a.anio,
        "tipo": a.tipo, "precio_usd": a.precio_usd, "stock": a.stock,
        "color": a.color, "combustible": a.combustible,
    }


def ejecutar_tool(db: Session, nombre: str, args: dict) -> str:
    """Ejecuta la herramienta y devuelve un JSON. Los errores de negocio
    se devuelven como dato para que Claude pueda explicárselos al cliente."""
    try:
        if nombre == "buscar_autos":
            autos = services.buscar_autos(db, **args)
            resultado = [_auto_a_dict(a) for a in autos]
        elif nombre == "ver_horarios":
            fecha = date.fromisoformat(args["fecha"])
            resultado = {"horarios_libres": services.horarios_disponibles(db, args["auto_id"], fecha)}
        elif nombre == "agendar_test_drive":
            turno = services.agendar_test_drive(
                db,
                args["auto_id"],
                args["nombre_cliente"],
                args["telefono"],
                datetime.fromisoformat(args["fecha_hora"]),
            )
            resultado = {"turno_id": turno.id, "estado": turno.estado,
                         "fecha_hora": turno.fecha_hora.isoformat()}
        else:
            resultado = {"error": f"Herramienta desconocida: {nombre}"}
    except services.ErrorNegocio as e:
        resultado = {"error": e.mensaje}
    except (ValueError, KeyError, TypeError) as e:
        resultado = {"error": f"Parámetros inválidos: {e}"}
    return json.dumps(resultado, ensure_ascii=False, default=str)
