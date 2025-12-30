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


# ----------------------------- CLEAR SCREEN ------------------------------

def clear_screen():
    """Clear the terminal using ANSI escape codes."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ----------------------------- DRAW HELPERS ------------------------------

def colorize_tile(ch: str) -> str:
    """Return a colored version of a map tile."""
    color = TILE_COLORS.get(ch, RESET)
    return f"{color}{ch}{RESET}"


def draw_grid(grid):
    """Render the dungeon grid with colors."""
    for row in grid:
        colored_row = (colorize_tile(ch) for ch in row)
        print("".join(colored_row))


def draw_hud(game):
    """Render the HUD (stats, upgrades, messages)."""
    p = game.player
    upgrades = game.progress["upgrades"]

    status = (
        f"Idle Roguelite  |  Floor {game.floor}  |  "
        f"Speed: {game.speed_mode} {'(PAUSED)' if game.paused else ''}"
    )

    stats = (
        f"HP {p.hp}/{p.max_hp}  "
        f"ATK {p.atk}  DEF {p.df}  "
        f"Regen {p.regen:.2f}/tick  "
        f"Gold {p.gold}  Kills {p.kills}"
    )

    up_text = (
        f"Upgrades: HP+{upgrades['hp']}  "
        f"ATK+{upgrades['atk']}  "
        f"DEF+{upgrades['def']}  "
        f"Regen+{upgrades['regen']}"
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
        grid[y][x] = MONSTER

    # Exit
    ex, ey = game.exit
    grid[ey][ex] = EXIT

    # Player
    px, py = game.player.x, game.player.y
    grid[py][px] = PLAYER

    # Draw everything
    draw_hud(game)
    draw_grid(grid)
    draw_footer(game)
