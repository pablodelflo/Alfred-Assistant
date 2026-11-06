"""Lectura y validación de la configuración del servidor."""
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

RUTA_POR_DEFECTO = Path("config/servidor.toml")


class ErrorConfig(Exception):
    pass


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    url_bd: str
    zona_temporal: Path


def ruta_config() -> Path:
    return Path(os.environ.get("ALFRED_CONFIG", RUTA_POR_DEFECTO))


def cargar(ruta: Path | None = None) -> Config:
    ruta = ruta or ruta_config()
    if not ruta.is_file():
        raise ErrorConfig(
            f"No existe {ruta}. Copia config.ejemplo/servidor.ejemplo.toml a esa ruta."
        )
    try:
        datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
        return Config(
            host=datos["servidor"].get("host", "127.0.0.1"),
            port=int(datos["servidor"].get("port", 8000)),
            url_bd=datos["base_datos"]["url"],
            zona_temporal=Path(
                datos.get("almacenamiento", {}).get("zona_temporal", "datos/temporal")
            ),
        )
    except (tomllib.TOMLDecodeError, KeyError, ValueError) as e:
        raise ErrorConfig(f"Configuración inválida en {ruta}: {e!r}") from e
