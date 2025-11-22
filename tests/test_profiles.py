from src.services.profiles import ProfileStore

def test_profile_roundtrip(tmp_path):
    store = ProfileStore(str(tmp_path / "profiles.json"))
    p = store.get("Tester")
    p.color = (1,2,3)
    store.save()
    s2 = ProfileStore(str(tmp_path / "profiles.json"))
    p2 = s2.get("Tester")
    assert p2.color == (1,2,3)