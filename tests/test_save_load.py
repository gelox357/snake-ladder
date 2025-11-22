import os
from src.services.persistence import save, load

def test_save_roundtrip(tmp_path):
    path = tmp_path / "game.json"
    save(str(path), {"a":1})
    d = load(str(path))
    assert d["a"] == 1