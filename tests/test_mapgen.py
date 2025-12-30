# tests/test_mapgen.py
from src.dungeon.mapgen import make_empty_map, place_rooms, all_floor_positions

def test_room_generation():
    grid = make_empty_map(40, 20)
    rooms = place_rooms(grid)
    floors = all_floor_positions(grid)
    assert len(rooms) > 0
    assert len(floors) > 0
    for (x, y) in floors:
        assert grid[y][x] == '.'  # FLOOR tile