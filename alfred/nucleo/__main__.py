"""Arranque del servidor: python -m alfred.nucleo"""
import sys

import uvicorn

from alfred.nucleo.arranque.requisitos import comprobar_todo
from alfred.nucleo.web.app import crear_app


def main() -> int:
    ok, config, resultados = comprobar_todo()
    for r in resultados:
        print(("[ok]    " if r.ok else "[FALLO] ") + r.mensaje)
    if not ok:
        print("\nNo se puede arrancar: corrige los fallos de arriba.")
        return 1
    uvicorn.run(crear_app(), host=config.host, port=config.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
