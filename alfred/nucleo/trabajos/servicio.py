"""Operaciones sobre trabajos. Es el único sitio que cambia estados."""
from sqlalchemy.orm import Session

from alfred.nucleo.actividad.registro import registrar
from alfred.nucleo.datos.modelos import Trabajo, ahora
from alfred.nucleo.trabajos.estados import Estado, es_final, transicion_valida


class TransicionInvalida(Exception):
    pass


def crear_trabajo(sesion: Session, minijob_id: str, entradas: dict | None = None) -> Trabajo:
    trabajo = Trabajo(minijob_id=minijob_id, entradas=entradas or {},
                      estado=Estado.PENDIENTE.value)
    sesion.add(trabajo)
    sesion.flush()  # asigna el id
    registrar(sesion, "trabajo.creado", f"Trabajo de {minijob_id} creado", trabajo_id=trabajo.id)
    return trabajo


def cambiar_estado(sesion: Session, trabajo: Trabajo, destino: Estado, *,
                   error_usuario: str | None = None, error_tecnico: str | None = None) -> None:
    """Valida la transición, actualiza marcas de tiempo y deja rastro en la actividad.

    No hace commit: lo decide quien llama.
    """
    origen = Estado(trabajo.estado)
    if not transicion_valida(origen, destino):
        raise TransicionInvalida(f"{origen.value} -> {destino.value} no está permitido")

    trabajo.estado = destino.value
    if destino is Estado.EN_CURSO:
        trabajo.iniciado_en = ahora()
        trabajo.terminado_en = None
    if destino is Estado.PENDIENTE:  # reintento tras interrupción
        trabajo.iniciado_en = None
        trabajo.terminado_en = None
        trabajo.progreso = 0
        trabajo.mensaje_progreso = None
    if es_final(destino):
        trabajo.terminado_en = ahora()
    if error_usuario is not None:
        trabajo.error_usuario = error_usuario
    if error_tecnico is not None:
        trabajo.error_tecnico = error_tecnico

    registrar(sesion, "trabajo.estado", f"{origen.value} -> {destino.value}",
              detalle={"origen": origen.value, "destino": destino.value},
              trabajo_id=trabajo.id)
    sesion.flush()
