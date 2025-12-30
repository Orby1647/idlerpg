# tests/test_game.py
from src.game import Game
from src.progress import DEFAULT_PROGRESS

def test_game_initializes():
    g = Game(DEFAULT_PROGRESS.copy())
    assert g.player.is_alive()
    assert g.grid is not None

def test_game_tick_runs():
    g = Game(DEFAULT_PROGRESS.copy())
    g.tick()
    assert g.player.hp > 0
