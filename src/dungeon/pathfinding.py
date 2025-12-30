from heapq import heappop, heappush
from mapgen import WALL

def neighbors4(x, y, w, h):
    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < w and 0 <= ny < h:
            yield (nx, ny)

def astar(grid, start, goals, blocked=set()):
    """Return path (list of (x,y)) from start to nearest goal using A*."""
    w, h = len(grid[0]), len(grid)
    goals = set(goals)
    if not goals:
        return None
    def hfun(a):
        # heuristic to nearest goal (Manhattan)
        return min(abs(a[0]-gx) + abs(a[1]-gy) for gx, gy in goals)

    openq = []
    heappush(openq, (0 + hfun(start), 0, start, None))
    came = {}
    gscore = {start: 0}
    seen = set()

    while openq:
        f, g, node, parent = heappop(openq)
        if node in seen:
            continue
        came[node] = parent
        seen.add(node)
        if node in goals:
            # Reconstruct path
            path = [node]
            cur = node
            while came[cur] is not None:
                cur = came[cur]
                path.append(cur)
            path.reverse()
            return path
        x, y = node
        for nx, ny in neighbors4(x, y, w, h):
            if grid[ny][nx] == WALL:
                continue
            if (nx, ny) in blocked:
                continue
            ng = g + 1
            if (nx, ny) not in gscore or ng < gscore[(nx, ny)]:
                gscore[(nx, ny)] = ng
                heappush(openq, (ng + hfun((nx, ny)), ng, (nx, ny), node))
    return None