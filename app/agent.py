import os
from datetime import date, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .tools import TOOLS, ejecutar_tool

load_dotenv()
client = Anthropic()  # lee ANTHROPIC_API_KEY del entorno
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_ITERACIONES = 6

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _calendario() -> str:
    hoy = date.today()
    dias = []
    for d in range(15):
        f = hoy + timedelta(days=d)
        etiqueta = " (HOY)" if d == 0 else ""
        dias.append(f"- {DIAS[f.weekday()]} {f.isoformat()}{etiqueta}")
    return "\n".join(dias)


def _system_prompt() -> str:
    return f"""Sos el asistente virtual de una concesionaria de autos en Argentina.

Calendario de los próximos 15 días (usalo SIEMPRE para interpretar "mañana", "el viernes", "el sábado", etc. Nunca calcules fechas por tu cuenta):
{_calendario()}

Reglas:
- Respondé en español rioplatense, tono cordial y breve. Saludá solo en el primer mensaje de la conversación.
- Para cualquier dato de autos, precios, stock u horarios, usá SIEMPRE las herramientas. Nunca inventes datos.
- No inventes políticas, requisitos ni datos de la concesionaria que no surjan de las herramientas.
- Los precios están en USD.
- Para agendar un test drive necesitás: auto, fecha, hora, nombre y teléfono. Pedí lo que falte y confirmá los datos con el cliente antes de llamar a agendar_test_drive.
- La concesionaria atiende de lunes a sábado, de 9 a 18 hs. Los turnos duran 1 hora.
- Si un auto no tiene stock, ofrecé alternativas del mismo tipo (usá buscar_autos con ese tipo).
- Si una herramienta devuelve un error, explicáselo al cliente y ofrecé una alternativa.
- Si te preguntan algo que no tiene que ver con la concesionaria, decí amablemente que solo podés ayudar con autos y test drives."""

def responder(db: Session, historial: list) -> str:
    """Recibe el historial de la conversación (se modifica in-place) y devuelve la respuesta final."""
    for _ in range(MAX_ITERACIONES):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=_system_prompt(),
            tools=TOOLS,
            messages=historial,
        )
        historial.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in resp.content]})

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        resultados = []
        for bloque in resp.content:
            if bloque.type == "tool_use":
                salida = ejecutar_tool(db, bloque.name, bloque.input)
                resultados.append({
                    "type": "tool_result",
                    "tool_use_id": bloque.id,
                    "content": salida,
                })
        historial.append({"role": "user", "content": resultados})

    return "Perdón, me trabé procesando tu consulta. ¿Podés reformularla?"
