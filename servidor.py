"""Servidor FastAPI: expone cada agente A2A en su propio puerto.

Uso:
    python servidor.py horarios     -> puerto 8001
    python servidor.py devoluciones -> puerto 8002
    python servidor.py supervisor   -> puerto 8003

Endpoints:
    GET  /ficha   -> la AgentCard del agente
    POST /a2a     -> {"pregunta": "..."} y responde {"respuesta": "..."}
"""

from __future__ import annotations

import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.a2a.agent import (  # noqa: E402
    PUERTOS,
    responder_devoluciones,
    responder_horarios,
    responder_supervisor,
)
from src.a2a.ficha import DEVOLUCIONES, HORARIOS, SUPERVISOR  # noqa: E402


class Pregunta(BaseModel):
    pregunta: str


def _ficha(nombre: str) -> dict:
    if nombre == "horarios":
        return HORARIOS
    if nombre == "devoluciones":
        return DEVOLUCIONES
    return SUPERVISOR


def _handlers(nombre: str):
    if nombre == "horarios":
        return responder_horarios
    if nombre == "devoluciones":
        return responder_devoluciones
    return responder_supervisor


def crear_app(nombre: str) -> FastAPI:
    app = FastAPI(title=f"Agente A2A: {nombre}")
    handler = _handlers(nombre)

    @app.get("/ficha")
    def ficha():
        return {"ficha": {k: v for k, v in _ficha(nombre).items() if k != "datos"}}

    @app.post("/a2a")
    def a2a(payload: Pregunta):
        resultado = handler(payload.pregunta)
        return JSONResponse(resultado)

    return app


def main() -> int:
    import uvicorn

    if len(sys.argv) < 2 or sys.argv[1] not in PUERTOS:
        print("Uso: python servidor.py {horarios|devoluciones|supervisor}")
        return 2

    nombre = sys.argv[1]
    puerto = PUERTOS[nombre]
    app = crear_app(nombre)
    print(f"[{nombre}] arriba en http://127.0.0.1:{puerto}")
    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
