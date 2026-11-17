"""Lógica de los tres agentes y el protocolo A2A mínimo.

A2A se implementa aquí como llamadas HTTP (httpx) entre agentes:
- El especialista expone un endpoint `/a2a` que recibe {"pregunta": ...} y
  devuelve {"respuesta": ...}.
- El supervisor, al responder, consulta las fichas y llama al especialista
  elegido por HTTP (mismo proceso que haría un cliente A2A real).
"""

from __future__ import annotations

from typing import Any

import httpx

from .ficha import DEVOLUCIONES, HORARIOS, ESPECIALISTAS, SUPERVISOR

# Puertos por agente (deben coincidir con servidor.py).
PUERTOS: dict[str, int] = {
    "horarios": 8001,
    "devoluciones": 8002,
    "supervisor": 8003,
}


# ---------------------------------------------------------------------------
# Respuesta de cada especialista (datos inventados, sin LLM).
# ---------------------------------------------------------------------------

def responder_horarios(pregunta: str) -> dict:
    d = HORARIOS["datos"]
    return {
        "respuesta": (
            f"Horarios de la tienda: lunes a viernes {d['lunes a viernes']}, "
            f"sabado {d['sabado']}, domingo y feriados {d['domingo y feriados']}."
        )
    }


def responder_devoluciones(pregunta: str) -> dict:
    d = DEVOLUCIONES["datos"]
    return {
        "respuesta": (
            f"Politica de devoluciones: plazo {d['plazo']}; requisitos: "
            f"{d['requisitos']}; {d['cambios']}."
        )
    }


# --- Determinación del especialista (reglas, sin LLM) ------------------------

_PALABRAS_HORARIOS = ("hora", "horario", "abre", "cierra", "apertura", "atencion")
_PALABRAS_DEVOLUCIONES = ("devol", "cambio", "reembol", "garantia", "talla", "boleta")


def _elegir_especialista(pregunta: str) -> tuple[str, str]:
    """Devuelve (especialista, motivo); especialista == '' si ninguno sirve."""
    p = pregunta.lower()
    if any(k in p for k in _PALABRAS_HORARIOS):
        return "horarios", (
            "La consulta menciona horarios de atencion, que es lo que sabe "
            "el agente 'horarios'."
        )
    if any(k in p for k in _PALABRAS_DEVOLUCIONES):
        return "devoluciones", (
            "La consulta menciona devolucion o cambio, que es lo que sabe "
            "el agente 'devoluciones'."
        )
    return "", "Ningun especialista coincide con la consulta."


# ---------------------------------------------------------------------------
# Supervisor: lee fichas, elige, llama por HTTP.
# ---------------------------------------------------------------------------

def leer_fichas() -> list[dict[str, Any]]:
    """Lee las fichas de los especialistas (nombre, descripcion, skills)."""
    fichas = []
    for nombre in ESPECIALISTAS:
        base = f"http://127.0.0.1:{PUERTOS[nombre]}"
        try:
            r = httpx.get(f"{base}/ficha", timeout=3.0)
            r.raise_for_status()
            fichas.append(r.json()["ficha"])
        except Exception as exc:  # noqa: BLE001
            fichas.append({"nombre": nombre, "error": f"{type(exc).__name__}"})
    return fichas


def llamar_especialista(nombre: str, pregunta: str) -> dict:
    """Llama al especialista por A2A (HTTP) y devuelve su respuesta."""
    base = f"http://127.0.0.1:{PUERTOS[nombre]}"
    r = httpx.post(f"{base}/a2a", json={"pregunta": pregunta}, timeout=10.0)
    r.raise_for_status()
    return r.json()


def responder_supervisor(pregunta: str, detalle: bool = False) -> dict:
    """Orquesta: elige especialista, llama y responde; o indica que no aplica."""
    especialista, motivo = _elegir_especialista(pregunta)

    pasos: list[str] = []
    fichas = leer_fichas()
    pasos.append(f"leidas {len(fichas)} fichas")

    if especialista:
        pasos.append(f"elegido: {especialista} (motivo: {motivo})")
        respuesta = llamar_especialista(especialista, pregunta)["respuesta"]
        pasos.append(f"llamado por A2A a {especialista}")
    else:
        disponibles = ", ".join(f["nombre"] for f in fichas if "error" not in f)
        pasos.append("elegido: ninguno (motivo: " + motivo + ")")
        respuesta = (
            "No tengo un especialista para esa consulta. "
            f"Especialistas disponibles: {disponibles}."
        )

    return {
        "respuesta": respuesta,
        "elegido": especialista,
        "motivo": motivo,
        "pasos": pasos,
    }
