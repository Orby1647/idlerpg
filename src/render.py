# src/render.py

import sys
from src.colors import (
    RESET, BOLD, DIM,
    FG_RED, FG_GREEN, FG_YELLOW, FG_CYAN, FG_MAGENTA, FG_WHITE
)
from src.dungeon.constants import (
    WALL, FLOOR, EXIT, COIN, POTION, PLAYER, MONSTER
)

# ----------------------------- COLOR HELPERS ------------------------------

TILE_COLORS = {
    WALL: FG_WHITE + DIM,
    FLOOR: RESET,
    PLAYER: FG_CYAN + BOLD,
    MONSTER: FG_RED + BOLD,
    COIN: FG_YELLOW + BOLD,
    POTION: FG_MAGENTA + BOLD,
    EXIT: FG_GREEN + BOLD,
}

def green(t):  return FG_GREEN + str(t) + RESET
def red(t):    return FG_RED + str(t) + RESET
def yellow(t): return FG_YELLOW + str(t) + RESET
def cyan(t):   return FG_CYAN + str(t) + RESET
def mag(t):    return FG_MAGENTA + str(t) + RESET
def white(t):  return FG_WHITE + str(t) + RESET


# ----------------------------- CLEAR SCREEN ------------------------------

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ----------------------------- TILE COLORING ------------------------------

def colorize_tile(ch, visible=False, explored=False, flash=False):
    """Return the correct colored tile based on fog + flash."""
    if not explored:
        return " "  # completely unseen

    if not visible:
        return FG_WHITE + DIM + ch + RESET  # explored but not visible

    if flash:
        return FG_RED + BOLD + ch + RESET

    color = TILE_COLORS.get(ch, RESET)
    return f"{color}{ch}{RESET}"


# ----------------------------- HP BAR ------------------------------------

def hp_bar(current, maximum, width=20):
    ratio = current / maximum
    filled = int(ratio * width)
    empty = width - filled

    if ratio > 0.6:
        color = FG_GREEN
    elif ratio > 0.3:
        color = FG_YELLOW
    else:
        color = FG_RED + BOLD

    return f"{color}{'█' * filled}{RESET}{DIM}{'░' * empty}{RESET}"


# ----------------------------- HUD ---------------------------------------

def draw_hud(game):
    p = game.player
    upgrades = game.progress["upgrades"]

    status = (
        f"Idle Roguelite  |  Floor {cyan(game.floor)}  |  "
        f"Speed: {yellow(game.speed_mode)} {red('(PAUSED)') if game.paused else ''}"
    )

    hpbar = hp_bar(p.hp, p.max_hp)

    hp_color = (
        green(p.hp) if p.hp > p.max_hp * 0.6 else
        yellow(p.hp) if p.hp > p.max_hp * 0.3 else
        red(p.hp)
    )

    stats = (
        f"HP {hp_color}/{green(p.max_hp)}  {hpbar}  "
        f"ATK {yellow(p.atk)}  DEF {cyan(p.df)}  "
        f"Regen {mag(f'{p.regen:.2f}')}/tick  "
        f"Gold {yellow(p.gold)}  Kills {red(p.kills)}"
    )

    up_text = (
        f"Upgrades: HP+{green(upgrades['hp'])}  "
        f"ATK+{yellow(upgrades['atk'])}  "
        f"DEF+{cyan(upgrades['def'])}  "
        f"Regen+{mag(upgrades['regen'])}"
    )

    controls = "Controls: P pause/resume | 1/2/3 speed | Q quit"

    print(status)
    print(stats)
    print(up_text)
    print(controls)

    if game.message:
        print(f"Event: {game.message}")
    else:
        print("")


# ----------------------------- FOOTER ------------------------------------

def draw_footer(game):
    res = game.result()
    if res == "running":
        print("\nWatching the runner...")
    elif res == "dead":
        print("\n💀 The runner died! Gold banked.")
    elif res == "escaped":
        print("\n🚪 The runner escaped! Gold banked.")


# ----------------------------- GRID RENDER --------------------------------

def draw_grid(grid):
    for row in grid:
        print("".join(row))


# ----------------------------- MAIN DRAW ---------------------------------

def draw(game):
    clear_screen()

    # Build fog-aware grid
    fog_grid = []
    for y, row in enumerate(game.grid):
        fog_row = []
        for x, ch in enumerate(row):
            visible = (x, y) in game.visible
            explored = (x, y) in game.explored
            fog_row.append([ch, visible, explored, False])  # flash=False for now
        fog_grid.append(fog_row)

    # Overlay items
    for (x, y) in game.coins:
        fog_grid[y][x][0] = COIN
    for (x, y) in game.potions:
        fog_grid[y][x][0] = POTION

    # Monsters
    for (x, y), mon in game.monsters.items():
        fog_grid[y][x][0] = MONSTER
        fog_grid[y][x][3] = mon.flash > 0

    # Exit
    ex, ey = game.exit
    fog_grid[ey][ex][0] = EXIT

    # Player
    px, py = game.player.x, game.player.y
    fog_grid[py][px][0] = PLAYER
    fog_grid[py][px][3] = game.player.flash > 0

    # Convert fog grid to colored strings
    colored_grid = []
    for row in fog_grid:
        out = []
        for ch, visible, explored, flash in row:
            out.append(colorize_tile(ch, visible, explored, flash))
        colored_grid.append(out)

    # Draw everything
    draw_hud(game)
    draw_grid(colored_grid)
    draw_footer(game)

    # Decrement flash AFTER drawing
    if game.player.flash > 0:
        game.player.flash -= 1
    for mon in game.monsters.values():
        if mon.flash > 0:
            mon.flash -= 1
