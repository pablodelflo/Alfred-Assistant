"""Comprobación de requisitos al arrancar."""
import sys
from dataclasses import dataclass

from alfred.nucleo.config.lectura import Config, ErrorConfig, cargar

PYTHON_MINIMO = (3, 13)
POSTGRES_MINIMO = 14


@dataclass
class Resultado:
    ok: bool
    mensaje: str


def comprobar_python() -> Resultado:
    v = sys.version_info
    if (v.major, v.minor) < PYTHON_MINIMO:
        return Resultado(False, f"Python {v.major}.{v.minor} detectado; se requiere {PYTHON_MINIMO[0]}.{PYTHON_MINIMO[1]} o superior.")
    return Resultado(True, f"Python {v.major}.{v.minor}.{v.micro}")


def comprobar_postgres(config: Config) -> Resultado:
    try:
        import psycopg
    except ImportError:
        return Resultado(False, "Falta psycopg. Ejecuta: pip install -e .")
    try:
        with psycopg.connect(config.url_bd, connect_timeout=5) as con:
            version = con.info.server_version // 10000
    except Exception as e:
        return Resultado(False, f"No se pudo conectar a PostgreSQL ({type(e).__name__}). Revisa base_datos.url en la configuración.")
    if version < POSTGRES_MINIMO:
        return Resultado(False, f"PostgreSQL {version} detectado; se requiere {POSTGRES_MINIMO} o superior.")
    return Resultado(True, f"PostgreSQL {version}")


def comprobar_zona_temporal(config: Config) -> Resultado:
    try:
        config.zona_temporal.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return Resultado(False, f"No se puede crear la zona temporal {config.zona_temporal}: {e}")
    return Resultado(True, f"Zona temporal: {config.zona_temporal}")


def comprobar_todo() -> tuple[bool, Config | None, list[Resultado]]:
    resultados = [comprobar_python()]
    try:
        config = cargar()
    except ErrorConfig as e:
        resultados.append(Resultado(False, str(e)))
        return False, None, resultados
    resultados.append(Resultado(True, "Configuración cargada"))
    resultados.append(comprobar_postgres(config))
    resultados.append(comprobar_zona_temporal(config))
    return all(r.ok for r in resultados), config, resultados
