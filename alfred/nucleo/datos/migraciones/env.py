"""Entorno de Alembic: la URL llega por config.attributes['conexion'] o desde servidor.toml."""
from alembic import context

from alfred.nucleo.datos import modelos  # noqa: F401  (registra las tablas)
from alfred.nucleo.datos.base import Base, crear_motor

config = context.config
target_metadata = Base.metadata


def ejecutar() -> None:
    conexion = config.attributes.get("conexion")
    if conexion is not None:
        _migrar(conexion)
        return
    from alfred.nucleo.config.lectura import cargar
    motor = crear_motor(cargar().url_bd)
    with motor.connect() as con:
        _migrar(con)


def _migrar(con) -> None:
    context.configure(connection=con, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
    con.commit()


ejecutar()
