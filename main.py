"""CLI de los tres agentes A2A.

Uso:
    python main.py horarios "pregunta"      (o devoluciones, o supervisor)
    python main.py supervisor "pregunta" --saltos
    python main.py supervisor --diagrama
"""

from __future__ import annotations

import argparse
import sys


def _cmd(nombre: str, pregunta: str, saltos: bool):
    from src.a2a.agent import (
        responder_devoluciones,
        responder_horarios,
        responder_supervisor,
    )

    if nombre == "horarios":
        resultado = {"respuesta": responder_horarios(pregunta)["respuesta"], "elegido": nombre}
    elif nombre == "devoluciones":
        resultado = {"respuesta": responder_devoluciones(pregunta)["respuesta"], "elegido": nombre}
    else:
        resultado = responder_supervisor(pregunta, detalle=True)

    if saltos:
        if nombre == "supervisor":
            for paso in resultado.get("pasos", []):
                print(f"  - {paso}")
            print()
        else:
            print(f"  - nodo: {nombre} (responde directo con sus datos)")
            print()

    print(resultado["respuesta"])


def _diagrama(nombre: str):
    from typing import TypedDict

    from langgraph.graph import StateGraph, END

    from src.a2a.agent import _elegir_especialista  # noqa: F401

    class Estado(TypedDict, total=False):
        pregunta: str
        respuesta: str
        elegido: str
        saltos: list

    g = StateGraph(Estado)

    def nodo_respuesta(state: Estado):
        return {"respuesta": "..."}

    if nombre == "supervisor":
        def elegir(state: Estado):
            esp, _ = _elegir_especialista(state.get("pregunta", ""))
            return {"elegido": esp}
        g.add_node("entrada", lambda s: {})
        g.add_node("elegir", elegir)
        g.add_node("llamar", nodo_respuesta)
        g.add_node("responder", nodo_respuesta)
        g.set_entry_point("entrada")
        g.add_edge("entrada", "elegir")
        g.add_conditional_edges(
            "elegir",
            lambda s: "llamar" if s.get("elegido") else "responder",
            {"llamar": "llamar", "responder": "responder"},
        )
        g.add_edge("llamar", "responder")
    else:
        g.add_node("entrada", lambda s: {})
        g.add_node("responder", nodo_respuesta)
        g.set_entry_point("entrada")
        g.add_edge("entrada", "responder")

    g.add_edge("responder", END)
    print(g.compile().get_graph().draw_mermaid())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Agentes A2A (horarios, devoluciones, supervisor).")
    parser.add_argument("agente", choices=["horarios", "devoluciones", "supervisor"])
    parser.add_argument("pregunta", nargs="?")
    parser.add_argument("--saltos", action="store_true")
    parser.add_argument("--diagrama", action="store_true")
    args = parser.parse_args(argv)

    if args.diagrama:
        _diagrama(args.agente)
        return 0

    if not args.pregunta:
        print('Uso: python main.py %s "pregunta"' % args.agente)
        return 2

    _cmd(args.agente, args.pregunta, args.saltos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
