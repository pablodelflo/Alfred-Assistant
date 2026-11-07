import pytest

from alfred.nucleo.trabajos.estados import FINALES, TRANSICIONES, Estado, es_final, transicion_valida

E = Estado


def test_todos_los_estados_tienen_transiciones_definidas():
    assert set(TRANSICIONES) == set(Estado)


def test_flujo_normal():
    assert transicion_valida(E.PENDIENTE, E.EN_CURSO)
    assert transicion_valida(E.EN_CURSO, E.TERMINADO)
    assert transicion_valida(E.EN_CURSO, E.TERMINADO_CON_AVISOS)


def test_cancelacion_pasa_por_cancelandose():
    assert transicion_valida(E.EN_CURSO, E.CANCELANDOSE)
    assert transicion_valida(E.CANCELANDOSE, E.CANCELADO)
    assert not transicion_valida(E.EN_CURSO, E.CANCELADO)


def test_interrumpido_solo_vuelve_a_pendiente():
    assert transicion_valida(E.INTERRUMPIDO, E.PENDIENTE)
    assert not transicion_valida(E.INTERRUMPIDO, E.EN_CURSO)


@pytest.mark.parametrize("estado", [E.TERMINADO, E.TERMINADO_CON_AVISOS, E.FALLIDO, E.CANCELADO])
def test_estados_finales_no_tienen_salida(estado):
    assert es_final(estado) and not TRANSICIONES[estado]


def test_interrumpido_no_es_final():
    assert E.INTERRUMPIDO not in FINALES
