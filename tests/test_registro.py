from pathlib import Path

import alfred.nucleo.minijobs.registro as reg


def _manifiesto(carpeta: Path, contenido: str):
    carpeta.mkdir(parents=True)
    (carpeta / "manifiesto.toml").write_text(contenido, encoding="utf-8")


def test_descubre_valido_e_ignora_invalido(tmp_path, monkeypatch):
    _manifiesto(tmp_path / "ok", 'id="ok"\nnombre="Ok"\ndescripcion="d"\ncategoria="c"\nversion="1"\n')
    _manifiesto(tmp_path / "roto", 'id="roto"\n')
    monkeypatch.setattr(reg, "_carpetas_base", lambda: [tmp_path])
    validos, avisos = reg.descubrir()
    assert [m.id for m in validos] == ["ok"]
    assert len(avisos) == 1 and "faltan campos" in avisos[0]


def test_dependencias_faltantes(monkeypatch):
    import importlib.util
    from alfred.nucleo.arranque import requisitos

    monkeypatch.setattr(importlib.util, "find_spec", lambda nombre: None)
    r = requisitos.comprobar_dependencias()
    assert not r.ok and "pip install -e ." in r.mensaje
