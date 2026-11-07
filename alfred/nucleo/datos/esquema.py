"""Gestión del esquema con Alembic (sin alembic.ini)."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, Engine

CARPETA = Path(__file__).parent / "migraciones"


def _config(conexion: Connection | None = None) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(CARPETA))
    if conexion is not None:
        cfg.attributes["conexion"] = conexion
    return cfg


def revision_cabeza() -> str | None:
    return ScriptDirectory.from_config(_config()).get_current_head()


def revision_actual(motor: Engine) -> str | None:
    with motor.connect() as con:
        return MigrationContext.configure(con).get_current_revision()


def actualizar(motor: Engine) -> None:
    with motor.connect() as con:
        command.upgrade(_config(con), "head")
