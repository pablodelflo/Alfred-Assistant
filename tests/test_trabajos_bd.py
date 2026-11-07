"""Servicio de trabajos sobre SQLite en memoria; el esquema real se prueba en test_esquema_postgres."""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from alfred.nucleo.datos.base import Base
from alfred.nucleo.datos.modelos import Actividad
from alfred.nucleo.trabajos.estados import Estado
from alfred.nucleo.trabajos.servicio import TransicionInvalida, cambiar_estado, crear_trabajo


@pytest.fixture
def sesion():
    motor = create_engine("sqlite://")
    Base.metadata.create_all(motor)
    with Session(motor) as s:
        yield s


def test_crear_trabajo_queda_pendiente_y_registra(sesion):
    t = crear_trabajo(sesion, "conversor_medios", {"calidad": 90})
    sesion.commit()
    assert t.estado == "pendiente" and t.entradas == {"calidad": 90}
    assert sesion.scalars(select(Actividad.tipo)).all() == ["trabajo.creado"]


def test_flujo_completo_marca_tiempos_y_registra(sesion):
    t = crear_trabajo(sesion, "x")
    cambiar_estado(sesion, t, Estado.EN_CURSO)
    assert t.iniciado_en is not None and t.terminado_en is None
    cambiar_estado(sesion, t, Estado.TERMINADO)
    assert t.terminado_en is not None
    assert sesion.scalars(select(Actividad.tipo)).all().count("trabajo.estado") == 2


def test_transicion_invalida_no_cambia_nada(sesion):
    t = crear_trabajo(sesion, "x")
    with pytest.raises(TransicionInvalida):
        cambiar_estado(sesion, t, Estado.TERMINADO)
    assert t.estado == "pendiente"


def test_interrumpido_se_reintenta_desde_cero(sesion):
    t = crear_trabajo(sesion, "x")
    cambiar_estado(sesion, t, Estado.EN_CURSO)
    t.progreso = 40
    cambiar_estado(sesion, t, Estado.INTERRUMPIDO)
    cambiar_estado(sesion, t, Estado.PENDIENTE)
    assert t.progreso == 0 and t.iniciado_en is None


def test_errores_en_dos_niveles(sesion):
    t = crear_trabajo(sesion, "x")
    cambiar_estado(sesion, t, Estado.EN_CURSO)
    cambiar_estado(sesion, t, Estado.FALLIDO, error_usuario="Fichero dañado", error_tecnico="Traceback...")
    assert t.error_usuario == "Fichero dañado" and t.error_tecnico == "Traceback..."
