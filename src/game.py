import random
from src.dungeon.mapgen import (make_empty_map, place_rooms, connect_rooms, carve_room,
                            room_center, bfs_distance, all_floor_positions)
from src.dungeon.constants import EXIT
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

    def _build_floor(self):
        # Stats from upgrades
        max_hp, atk, df, regen = derived_stats(self.progress)
        self.grid = make_empty_map(MAP_W, MAP_H)
        rooms = place_rooms(self.grid)
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
        self.grid[ey][ex] = EXIT

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
        mscale = 1.0 + (self.floor-1) * (0.15 * FLOORSCALE())  # mild scaling
        for (mx, my) in mons_tiles:
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
        # regen
        self.player.tick_regen()
        # If fighting, resolve one combat round
        if self.fighting:
            mpos = self.fighting
            mon = self.monsters.get(mpos)
            if mon and mon.is_alive() and self.player.is_alive():
                self._combat_round(self.player, mon)
                if not mon.is_alive():
                    self.player.kills += 1
                    # drop small gold
                    self.player.gold += random.randint(2, 5)
                    del self.monsters[mpos]
                    self.fighting = None
                    self.message = f"Defeated monster at {mpos}"
            # If player died
            if not self.player.is_alive():
                return
            return

        # If standing on coin/potion, collect/use
        ppos = (self.player.x, self.player.y)
        if ppos in self.coins:
            self.coins.remove(ppos)
            g = random.randint(3, 8)
            self.player.gold += g
            self.message = f"Collected {g} gold"
        if ppos in self.potions:
            self.potions.remove(ppos)
            heal = random.randint(8, 16)
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            self.message = f"Drank potion (+{heal} HP)"

        # If reached exit, finish run
        if ppos == self.exit:
            return

        # Decide next target: prioritize potion if low, else coin, else exit
        targets = []
        if self.player.hp <= int(self.player.max_hp * 0.35) and self.potions:
            targets = list(self.potions)
        elif self.coins:
            targets = list(self.coins)
        else:
            targets = [self.exit]

        # Compute path; monsters are passable but will trigger combat if stepped into
        blocked = set()  # could add traps, etc.
        path = astar(self.grid, ppos, targets, blocked=blocked)
        self.path = path

        # Move one step along path
        if path and len(path) > 1:
            nx, ny = path[1]
            # If moving into a monster tile, start combat
            if (nx, ny) in self.monsters:
                self.fighting = (nx, ny)
                self.message = "Encounter!"
            else:
                self.player.x, self.player.y = nx, ny
        else:
            # No path found (rare) -> idle
            self.message = "No path"

    def _combat_round(self, p, m):
        # Player attacks
        dmg_p = max(1, p.atk - m.df)
        if random.random() < 0.10:  # crit chance
            dmg_p = int(dmg_p * 1.5)
            self.message = "Critical hit!"
        m.hp -= dmg_p
        m.flash = 2

        # Monster attacks if alive
        if m.hp > 0:
            dmg_m = max(1, m.atk - p.df)
            p.hp -= dmg_m
            p.flash = 2

    def is_over(self):
        return not self.player.is_alive() or (self.player.x, self.player.y) == self.exit

    def result(self):
        if (self.player.x, self.player.y) == self.exit:
            return "escaped"
        elif not self.player.is_alive():
            return "dead"
        return "running"

def FLOORSCALE():
    # tiny helper to allow tuning without changing constant names everywhere
    return FLOOR_SCALING
