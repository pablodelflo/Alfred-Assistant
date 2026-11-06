"""Registro de minijobs: descubre y valida los manifiestos."""
import tomllib
from dataclasses import dataclass
from pathlib import Path

import alfred.minijobs as paquete_minijobs

CAMPOS_OBLIGATORIOS = ("id", "nombre", "descripcion", "categoria", "version")


@dataclass(frozen=True)
class Minijob:
    id: str
    nombre: str
    descripcion: str
    categoria: str
    version: str


def _carpetas_base() -> list[Path]:
    base = Path(paquete_minijobs.__file__).parent
    return [base, Path("minijobs_personales")]


def descubrir() -> tuple[list[Minijob], list[str]]:
    """Devuelve (minijobs válidos, avisos de los inválidos)."""
    validos, avisos = [], []
    for carpeta in _carpetas_base():
        if not carpeta.is_dir():
            continue
        for manifiesto in sorted(carpeta.glob("*/manifiesto.toml")):
            try:
                datos = tomllib.loads(manifiesto.read_text(encoding="utf-8"))
                faltan = [c for c in CAMPOS_OBLIGATORIOS if c not in datos]
                if faltan:
                    raise ValueError(f"faltan campos: {', '.join(faltan)}")
                validos.append(Minijob(**{c: datos[c] for c in ("id", "nombre", "descripcion", "categoria", "version")}))
            except Exception as e:
                avisos.append(f"{manifiesto}: {e}")
    return validos, avisos
