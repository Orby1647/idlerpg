# tests/test_render.py
from src.render import draw
from src.game import Game
from src.progress import DEFAULT_PROGRESS

def test_draw_runs():
    g = Game(DEFAULT_PROGRESS.copy())
    draw(g)  # Should not raise
    assert True  # If we reach here, the test passes