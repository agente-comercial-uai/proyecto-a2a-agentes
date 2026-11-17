"""Fichas (AgentCard) de los tres agentes, según el protocolo A2A.

Cada ficha describe qué hace el agente. El supervisor lee las fichas de los
dos especialistas para decidir a cuál llamar. Formato intencionalmente mínima
y equivalente al concepto de AgentCard de A2A.
"""

from __future__ import annotations

from typing import Any

# --- Especialista 1: horarios ------------------------------------------------
HORARIOS: dict[str, Any] = {
    "nombre": "horarios",
    "descripcion": "Responde los horarios de atencion de la tienda.",
    "skills": [
        "horario de apertura y cierre",
        "dias de atencion",
        "horario de dias feriados",
    ],
    "datos": {
        "lunes a viernes": "09:00 a 19:00",
        "sabado": "10:00 a 14:00",
        "domingo y feriados": "cerrado",
    },
}

# --- Especialista 2: devoluciones --------------------------------------------
DEVOLUCIONES: dict[str, Any] = {
    "nombre": "devoluciones",
    "descripcion": "Responde la politica de devoluciones y cambios.",
    "skills": [
        "plazo para devolver un producto",
        "requisitos de una devolucion",
        "cambios de talla o producto",
    ],
    "datos": {
        "plazo": "30 dias desde la compra",
        "requisitos": "producto sin uso, con etiqueta y boleta",
        "cambios": "cambio de talla sujeto a stock disponible",
    },
}

# --- Supervisor --------------------------------------------------------------
SUPERVISOR: dict[str, Any] = {
    "nombre": "supervisor",
    "descripcion": "Recibe la consulta y decide a cual especialista llamar.",
    "skills": ["elegir entre horarios y devoluciones", "derivar la consulta"],
}

# Catálogo de especialistas que conoce el supervisor.
ESPECIALISTAS: tuple[str, ...] = ("horarios", "devoluciones")
