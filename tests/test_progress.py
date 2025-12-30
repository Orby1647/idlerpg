# tests/test_progress.py
from src.progress import derived_stats, DEFAULT_PROGRESS

def test_derived_stats_basic():
    p = DEFAULT_PROGRESS.copy()
    max_hp, atk, df, regen = derived_stats(p)
    assert max_hp == p["base"]["max_hp"]
    assert atk == p["base"]["atk"]
    assert df == p["base"]["def"]
    assert regen == p["base"]["regen"]