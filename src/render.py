import sys
from dungeon.mapgen import PLAYER, MONSTER, COIN, POTION, EXIT

def clear_screen():
    # Fast ANSI clear
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def draw(game):
    clear_screen()
    grid = [row[:] for row in game.grid]  # copy
    # Render items
    for (x, y) in game.coins: grid[y][x] = COIN
    for (x, y) in game.potions: grid[y][x] = POTION
    # Render monsters
    for (x, y), mon in game.monsters.items():
        grid[y][x] = MONSTER
    # Render exit
    ex, ey = game.exit
    grid[ey][ex] = EXIT
    # Render player
    px, py = game.player.x, game.player.y
    grid[py][px] = PLAYER

    # HUD
    p = game.player
    status = f"Idle Roguelite  |  Floor {game.floor}  |  Speed: {game.speed_mode} {'(PAUSED)' if game.paused else ''}"
    stats  = f"HP {p.hp}/{p.max_hp}  ATK {p.atk}  DEF {p.df}  Regen {p.regen:.2f}/tick  Gold {p.gold}  Kills {p.kills}"
    upgrades = game.progress["upgrades"]
    up_text = f"Upgrades: HP+{upgrades['hp']} ATK+{upgrades['atk']} DEF+{upgrades['def']} Regen+{upgrades['regen']}"
    controls = "Controls: P pause/resume | 1/2/3 speed | Q quit"

    print(status)
    print(stats)
    print(up_text)
    print(controls)
    if game.message:
        print(f"Event: {game.message}")
    else:
        print("")

    # Draw map
    for row in grid:
        print("".join(row))

    # Footer
    res = game.result()
    if res == "running":
        print("\nWatching the runner...")
    elif res == "dead":
        print("\n💀 The runner died! Gold banked.")
    elif res == "escaped":
        print("\n🚪 The runner escaped! Gold banked.")