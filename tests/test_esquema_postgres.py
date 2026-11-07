"""Prueba contra un PostgreSQL real. Se salta si no hay ALFRED_TEST_DB_URL.

Cuidado: BORRA las tablas de esa base de datos. Usa una base solo de pruebas.
"""
import os

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect, text

from alfred.nucleo.datos.base import Base, crear_motor
from alfred.nucleo.datos.esquema import actualizar, revision_actual, revision_cabeza

URL = os.environ.get("ALFRED_TEST_DB_URL")
pytestmark = pytest.mark.skipif(not URL, reason="sin ALFRED_TEST_DB_URL")


@pytest.fixture
def motor():
    m = crear_motor(URL)
    with m.begin() as con:
        con.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    return m


def test_migraciones_crean_el_esquema_y_coinciden_con_los_modelos(motor):
    assert revision_actual(motor) is None
    actualizar(motor)
    assert revision_actual(motor) == revision_cabeza()
    assert {"trabajos", "actividad"} <= set(inspect(motor).get_table_names())
    with motor.connect() as con:
        diferencias = compare_metadata(MigrationContext.configure(con), Base.metadata)
    assert diferencias == []


def test_actualizar_es_idempotente(motor):
    actualizar(motor)
    actualizar(motor)
    assert revision_actual(motor) == revision_cabeza()
