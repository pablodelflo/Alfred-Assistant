"""Gestión de la base de datos: python -m alfred.nucleo.datos [estado|actualizar]"""
import sys


def main(argv: list[str]) -> int:
    from alfred.nucleo.config.lectura import ErrorConfig, cargar
    from alfred.nucleo.datos.base import crear_motor
    from alfred.nucleo.datos.esquema import actualizar, revision_actual, revision_cabeza

    orden = argv[0] if argv else "estado"
    if orden not in ("estado", "actualizar"):
        print("Uso: python -m alfred.nucleo.datos [estado|actualizar]")
        return 2
    try:
        motor = crear_motor(cargar().url_bd)
        if orden == "actualizar":
            actualizar(motor)
            print("Esquema actualizado.")
        actual, cabeza = revision_actual(motor), revision_cabeza()
    except ErrorConfig as e:
        print(e)
        return 1
    except Exception as e:
        print(f"Error de base de datos: {e}")
        return 1
    print(f"Revisión actual: {actual or '(sin esquema)'} · última disponible: {cabeza}")
    return 0 if actual == cabeza else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
