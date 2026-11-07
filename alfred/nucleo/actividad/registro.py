"""Registro de actividad: una fila por acción o error relevante."""
import uuid

from sqlalchemy.orm import Session

from alfred.nucleo.datos.modelos import Actividad


def registrar(sesion: Session, tipo: str, mensaje: str, *,
              detalle: dict | None = None, trabajo_id: uuid.UUID | None = None) -> Actividad:
    fila = Actividad(tipo=tipo, mensaje=mensaje, detalle=detalle, trabajo_id=trabajo_id)
    sesion.add(fila)
    return fila
