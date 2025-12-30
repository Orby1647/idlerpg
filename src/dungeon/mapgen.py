import random
from collections import deque
from ..config import ROOM_MIN, ROOM_MAX, ROOM_ATTEMPTS
from .pathfinding import neighbors4

WALL, FLOOR = "#", "."
EXIT = "E"
COIN = "$"
POTION = "!"
PLAYER = "@"
MONSTER = "M"

def make_empty_map(w, h):
    return [[WALL for _ in range(w)] for _ in range(h)]

def carve_room(grid, x, y, rw, rh):
    for j in range(y, y+rh):
        for i in range(x, x+rw):
            if 0 <= i < len(grid[0]) and 0 <= j < len(grid):
                grid[j][i] = FLOOR

def place_rooms(grid):
    rooms = []
    for _ in range(ROOM_ATTEMPTS):
        rw = random.randint(ROOM_MIN, ROOM_MAX)
        rh = random.randint(ROOM_MIN, ROOM_MAX)
        x = random.randint(1, len(grid[0]) - rw - 2)
        y = random.randint(1, len(grid) - rh - 2)
        # Check overlap
        ok = True
        for (rx, ry, rw2, rh2) in rooms:
            if (x < rx+rw2+1 and x+rw+1 > rx and
                y < ry+rh2+1 and y+rh+1 > ry):
                ok = False
                break
        if ok:
            carve_room(grid, x, y, rw, rh)
            rooms.append((x, y, rw, rh))
    return rooms

def room_center(room):
    x, y, rw, rh = room
    return (x + rw//2, y + rh//2)

def carve_corridor(grid, ax, ay, bx, by):
    # Simple L-shaped corridor
    cx, cy = ax, ay
    dx = 1 if bx > ax else -1
    while cx != bx:
        grid[cy][cx] = FLOOR
        cx += dx
    dy = 1 if by > ay else -1
    while cy != by:
        grid[cy][cx] = FLOOR
        cy += dy
    grid[by][bx] = FLOOR

def connect_rooms(grid, rooms):
    if not rooms:
        return
    centers = [room_center(r) for r in rooms]
    # Connect each room to the nearest previous room (simple heuristic)
    connected = [centers[0]]
    for c in centers[1:]:
        nearest = min(connected, key=lambda k: abs(k[0]-c[0]) + abs(k[1]-c[1]))
        carve_corridor(grid, c[0], c[1], nearest[0], nearest[1])
        connected.append(c)

def all_floor_positions(grid):
    pos = []
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == FLOOR:
                pos.append((x, y))
    return pos

def bfs_distance(grid, start):
    w, h = len(grid[0]), len(grid)
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in neighbors4(x, y, w, h):
            if grid[ny][nx] != WALL and (nx, ny) not in dist:
                dist[(nx, ny)] = dist[(x, y)] + 1
                q.append((nx, ny))
    return dist