#!/usr/bin/env python3
# Idle Roguelite — watch a player auto-run dungeons with meta progression.
# Pure Python, cross-platform terminal. No external libraries required.

import time, random
from config import TICK_SPEEDS
from render import draw
from input import KeyReader
from progress import load_progress, save_progress, apply_auto_upgrades, derived_stats
from game import Game


def run_floor(progress):
    game = Game(progress)
    with KeyReader() as kr:
        while True:
            draw(game)
            if game.is_over():
                # Bank the gold and mark run
                progress["bank_gold"] += game.player.gold
                progress["runs"] += 1
                break
            # Input
            key = kr.read_key()
            if key:
                if key in ("q", "Q"):
                    # Save progress and exit whole program
                    progress["bank_gold"] += game.player.gold
                    progress["runs"] += 1
                    draw(game)
                    return False  # signal quit
                if key in ("p", "P"):
                    game.paused = not game.paused
                if key in ("1", "2", "3"):
                    game.speed_mode = {"1":"slow","2":"normal","3":"fast"}[key]

            # Sim tick
            game.tick()
            time.sleep(TICK_SPEEDS[game.speed_mode])
    return True  # floor complete (dead or escaped)

def main():
    random.seed()
    progress = load_progress()
    # Auto-spend banked gold on upgrades (policy can be tweaked)
    apply_auto_upgrades(progress)

    # Display summary
    max_hp, atk, df, regen = derived_stats(progress)
    print("Loading Idle Roguelite...")
    print(f"Runs completed: {progress['runs']}")
    print(f"Banked gold: {progress['bank_gold']}")
    print(f"Stats after upgrades: HP {max_hp} ATK {atk} DEF {df} Regen {regen:.2f}/tick")
    print("Starting floor in 2 seconds...")
    time.sleep(2)

    # Floor loop (keep watching new floors until quit)
    while True:
        keep_going = run_floor(progress)
        save_progress(progress)
        if not keep_going:
            print("\nProgress saved. Goodbye!")
            break
        # Between floors: auto-upgrade again
        apply_auto_upgrades(progress)
        max_hp, atk, df, regen = derived_stats(progress)
        print("\n--- Floor complete ---")
        print(f"Total runs: {progress['runs']}")
        print(f"Banked gold (after auto-upgrades): {progress['bank_gold']}")
        print(f"Stats: HP {max_hp} ATK {atk} DEF {df} Regen {regen:.2f}/tick")
        print("Next floor starts in 3 seconds... (press Ctrl+C to exit)")
        time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Progress saved if floor ended.")