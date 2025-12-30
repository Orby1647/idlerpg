# src/render.py

import sys
from src.colors import (
    RESET, BOLD, DIM,
    FG_RED, FG_GREEN, FG_YELLOW, FG_CYAN, FG_MAGENTA, FG_WHITE
)
from src.dungeon.constants import (
    WALL, FLOOR, EXIT, COIN, POTION, PLAYER, MONSTER
)


# ----------------------------- COLOR MAP ---------------------------------

TILE_COLORS = {
    WALL: FG_WHITE + DIM,
    FLOOR: RESET,
    PLAYER: FG_CYAN + BOLD,
    MONSTER: FG_RED + BOLD,
    COIN: FG_YELLOW + BOLD,
    POTION: FG_MAGENTA + BOLD,
    EXIT: FG_GREEN + BOLD,
}
def green(text):  return FG_GREEN + str(text) + RESET
def red(text):    return FG_RED + str(text) + RESET
def yellow(text): return FG_YELLOW + str(text) + RESET
def cyan(text):   return FG_CYAN + str(text) + RESET
def mag(text):    return FG_MAGENTA + str(text) + RESET
def white(text):  return FG_WHITE + str(text) + RESET


# ----------------------------- CLEAR SCREEN ------------------------------

def clear_screen():
    """Clear the terminal using ANSI escape codes."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ----------------------------- DRAW HELPERS ------------------------------

def colorize_tile(ch, flash=False):
    if flash:
        return f"{FG_RED}{BOLD}{ch}{RESET}"
    color = TILE_COLORS.get(ch, RESET)
    return f"{color}{ch}{RESET}"

def draw_grid(grid):
    for row in grid:
        out = []
        for cell in row:
            if isinstance(cell, tuple):
                ch, flash = cell
                out.append(colorize_tile(ch, flash))
            else:
                out.append(colorize_tile(cell))
        print("".join(out))

def hp_bar(current, maximum, width=20):
    ratio = current / maximum
    filled = int(ratio * width)
    empty = width - filled

    # Color transitions
    if ratio > 0.6:
        color = FG_GREEN
    elif ratio > 0.3:
        color = FG_YELLOW
    else:
        color = FG_RED + BOLD

    return f"{color}{'█' * filled}{RESET}{DIM}{'░' * empty}{RESET}"

def draw_hud(game):
    """Render the HUD (stats, upgrades, messages)."""
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


def draw_footer(game):
    """Render the footer showing run status."""
    res = game.result()
    if res == "running":
        print("\nWatching the runner...")
    elif res == "dead":
        print("\n💀 The runner died! Gold banked.")
    elif res == "escaped":
        print("\n🚪 The runner escaped! Gold banked.")


# ----------------------------- MAIN DRAW ---------------------------------

def draw(game):
    """Full render pass: HUD + map + footer."""
    clear_screen()

    # Copy grid so we can overlay items
    grid = [row[:] for row in game.grid]

    # Overlay items
    for (x, y) in game.coins:
        grid[y][x] = COIN
    for (x, y) in game.potions:
        grid[y][x] = POTION
    for (x, y), mon in game.monsters.items():
        grid[y][x] = (MONSTER, mon.flash > 0)

    # Exit
    ex, ey = game.exit
    grid[ey][ex] = EXIT

    # Player
    px, py = game.player.x, game.player.y
    grid[py][px] = (PLAYER, game.player.flash > 0)

    # Draw everything
    draw_hud(game)
    draw_grid(grid)
    draw_footer(game)

    if game.player.flash > 0: 
        game.player.flash -= 1 
    for mon in game.monsters.values(): 
        if mon.flash > 0: 
            mon.flash -= 1