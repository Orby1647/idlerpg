# tests/test_entities.py
from src.dungeon.entities import Player, Monster

def test_player_initialization():
    p = Player(1, 2, 30, 5, 1, 0.1)
    assert p.hp == 30
    assert p.atk == 5
    assert p.df == 1
    assert p.regen == 0.1
    assert p.x == 1
    assert p.y == 2