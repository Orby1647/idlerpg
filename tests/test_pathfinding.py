# tests/test_pathfinding.py
from src.dungeon.pathfinding import astar
from src.dungeon.constants import FLOOR

def test_astar_simple():
    grid = [[FLOOR]*5 for _ in range(5)]
    path = astar(grid, (0,0), [(4,4)])
    assert path[0] == (0,0)
    assert path[-1] == (4,4)
    assert len(path) > 1
def test_astar_blocked():
    grid = [[FLOOR]*5 for _ in range(5)]
    for i in range(5):
        grid[2][i] = '#'
    path = astar(grid, (0,0), [(4,4)])
    assert path is None
def test_astar_multiple_goals():
    grid = [[FLOOR]*5 for _ in range(5)]
    path = astar(grid, (0,0), [(4,4), (2,2)])
    assert path[-1] == (2,2)
    assert len(path) > 1