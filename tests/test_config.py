# tests/test_config.py
from src import config

def test_tick_speeds_exist():
    assert "normal" in config.TICK_SPEEDS
    assert config.TICK_SPEEDS["normal"] > 0
def test_room_size_settings():
    assert config.ROOM_MIN > 0
    assert config.ROOM_MAX >= config.ROOM_MIN
def test_map_dimensions():
    assert config.MAP_W > 0
    assert config.MAP_H > 0