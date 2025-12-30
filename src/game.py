import random
from src.dungeon.mapgen import (make_empty_map, place_rooms, connect_rooms, carve_room,
                            room_center, bfs_distance, all_floor_positions)
from src.dungeon.constants import EXIT, WALL, LOCKED_EXIT
from src.dungeon.pathfinding import astar
from src.config import (MAP_W, MAP_H, COIN_COUNT, POTION_COUNT, MONSTER_COUNT,
                    FLOOR_SCALING)
from src.dungeon.entities import Player, Monster
from src.progress import derived_stats

class Game:
    def __init__(self, progress):
        self.progress = progress
        self.floor = progress["runs"] + 1
        self.speed_mode = "normal"
        self.paused = False
        self.message = ""
        self._build_floor()
        self.visible = set()
        self.explored = set()
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.log = []

    def log_event(self, msg):
        self.log.append(msg)
        if len(self.log) > 5:
            self.log.pop(0)

    def _blocks_sight(self, x, y):
        return self.grid[y][x] == WALL

    def _bresenham_line(self, x0, y0, x1, y1):
        """Yield all tiles on the line from (x0,y0) to (x1,y1)."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            yield (x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def compute_visibility(self, radius=8):
        px, py = self.player.x, self.player.y
        self.visible.clear()
        # Always see your own tile
        self.visible.add((px, py))
        self.explored.add((px, py))
        for y in range(py - radius, py + radius + 1):
            for x in range(px - radius, px + radius + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    dx = x - px
                    dy = y - py
                    if dx*dx + dy*dy <= radius*radius:
                        # Cast a ray from player to (x,y)
                        blocked = False
                        for (lx, ly) in self._bresenham_line(px, py, x, y):
                            if self._blocks_sight(lx, ly) and (lx, ly) != (x, y):
                                blocked = True
                                break
                        if not blocked:
                            self.visible.add((x, y))
                            self.explored.add((x, y))

    def _build_floor(self):
        # Stats from upgrades
        max_hp, atk, df, regen = derived_stats(self.progress)
        self.grid = make_empty_map(MAP_W, MAP_H)
        rooms = place_rooms(self.grid)
        is_boss_floor = (self.floor % 5 == 0)
        self.exit_locked = is_boss_floor
        if not rooms:
            # ensure at least one room
            carve_room(self.grid, 2, 2, 8, 6)
            rooms = [(2,2,8,6)]
        connect_rooms(self.grid, rooms)
        floors = all_floor_positions(self.grid)

        # Player spawn at center of first room
        sx, sy = room_center(rooms[0])
        self.player = Player(sx, sy, max_hp, atk, df, regen)

        # Exit at farthest reachable floor tile
        dist = bfs_distance(self.grid, (sx, sy))
        far = max(dist.items(), key=lambda kv: kv[1])[0]
        self.exit = far
        ex, ey = self.exit
        self.grid[ey][ex] = LOCKED_EXIT if is_boss_floor else EXIT

        # Place coins
        open_tiles = [p for p in floors if p != (sx, sy) and p != self.exit]
        random.shuffle(open_tiles)
        self.coins = set(open_tiles[:COIN_COUNT])

        # Place potions
        pts = [p for p in open_tiles[COIN_COUNT:COIN_COUNT+POTION_COUNT]]
        self.potions = set(pts)

        # Place monsters
        mons_tiles = [p for p in open_tiles[COIN_COUNT+POTION_COUNT:
                                            COIN_COUNT+POTION_COUNT+MONSTER_COUNT]]
        self.monsters = {}

        if is_boss_floor:
            # Place a single boss monster
            mx, my = mons_tiles[0]
            hp = int(50 * (1.2 ** (self.floor // 5)))  # scale boss HP
            atk = int(10 * (1.1 ** (self.floor // 5)))
            df  = int(5 * (1.1 ** (self.floor // 5)))
            boss = Monster(mx, my, hp, atk, df)
            boss.is_boss = True
            self.monsters[(mx, my)] = boss
        else:
            # Regular monsters
            pass

        mscale = 1.0 + (self.floor-1) * (0.15 * FLOORSCALE())  # mild scaling
        for (mx, my) in mons_tiles:
            if is_boss_floor and (mx, my) in self.monsters:
                continue  # skip boss tile
            hp = int(12 * mscale + random.randint(-2, 2))
            atk = int(4 * mscale + random.randint(0, 2))
            df  = int(1 * mscale + random.randint(0, 1))
            self.monsters[(mx, my)] = Monster(mx, my, hp, atk, df)

        # combat state
        self.fighting = None  # (x,y) of monster currently engaged
        self.path = None      # current path being followed

    def tick(self):
        if self.paused:
            return
        self.player.tick_regen()
        if self._handle_combat():
            return
        ppos = (self.player.x, self.player.y)
        if self._handle_pickups(ppos):
            return
        if ppos == self.exit:
            if self.exit_locked:
                self.log_event("The exit is locked! Defeat the boss to unlock.")
                return
            return
        targets = self._choose_targets()
        self._move_along_path(ppos, targets)
        self.compute_visibility()

    def _handle_pickups(self, ppos):
        picked = False
        if ppos in self.coins:
            self.coins.remove(ppos)
            self.player.gold += 1
            self.log_event("Picked up a coin!")
            picked = True
        if ppos in self.potions:
            self.potions.remove(ppos)
            heal_amount = min(10, self.player.max_hp - self.player.hp)
            self.player.hp += heal_amount
            self.log_event(f"Drank a potion! Restored {heal_amount} HP.")
            picked = True
        return picked
    
    def _handle_combat(self):
        if self.fighting:
            mx, my = self.fighting
            monster = self.monsters.get((mx, my))
            if monster and monster.is_alive():
                self._combat_round(self.player, monster)
                if not monster.is_alive():
                    del self.monsters[(mx, my)]
                    self.player.kills += 1
                    if getattr(monster, "is_boss", False):
                        self.exit_locked = False
                        self.log_event("Boss defeated! The exit is now unlocked.")
                        ex, ey = self.exit
                        self.grid[ey][ex] = EXIT
                    else:
                        self.log_event("Monster defeated!")
                return True
            else:
                self.fighting = None
        return False
    
    def _choose_targets(self):
        """Return a list of target tiles based on player state."""
        low_hp = self.player.hp <= int(self.player.max_hp * 0.35)
        if low_hp and self.potions:
            return list(self.potions)
        if self.coins:
            return list(self.coins)
        return [self.exit]

    def _move_along_path(self, ppos, targets):
        blocked = set()  # future: traps, locked doors, hazards
        path = astar(self.grid, ppos, targets, blocked=blocked)
        self.path = path
        if not path or len(path) <= 1:
            self.log_event("No path")
            return
        nx, ny = path[1]
        if (nx, ny) in self.monsters:
            self.fighting = (nx, ny)
            mon = self.monsters[(nx, ny)]
            if getattr(mon, "is_boss", False):
                self.log_event("A boss appears!")
            else:
                self.log_event("Encounter!")
            return
        self.player.x, self.player.y = nx, ny

    def _combat_round(self, p, m):
        # Player attacks
        dmg_p = max(1, p.atk - m.df)
        if random.random() < 0.10:  # crit chance
            dmg_p = int(dmg_p * 1.5)
            self.log_event("Critical hit!")
        m.hp -= dmg_p
        m.flash = 2

        # Monster attacks if alive
        if m.hp > 0:
            dmg_m = max(1, m.atk - p.df)
            p.hp -= dmg_m
            p.flash = 2

    def is_over(self):
        if not self.player.is_alive():
            return True 
        at_exit = (self.player.x, self.player.y) == self.exit
        if at_exit and not self.exit_locked:
            return True
        return False

    def result(self):
        at_exit = (self.player.x, self.player.y) == self.exit
        exit_unlocked = not getattr(self, "exit_locked", False)
        if at_exit and exit_unlocked:
            return "escaped"
        elif not self.player.is_alive():
            return "dead"
        return "running"

def FLOORSCALE():
    # tiny helper to allow tuning without changing constant names everywhere
    return FLOOR_SCALING
