import json
import os

PROGRESS_FILE = "progress.json"
DEFAULT_PROGRESS = {
    "runs": 0,
    "bank_gold": 0,
    "upgrades": {"hp": 0, "atk": 0, "def": 0, "regen": 0},
    # Base stats before upgrades
    "base": {"max_hp": 28, "atk": 6, "def": 1, "regen": 0.0}
}
UPGRADE_COSTS = {"hp": 20, "atk": 30, "def": 30, "regen": 40}
UPGRADE_EFFECT = {"hp": 6, "atk": 1, "def": 1, "regen": 0.10}
AUTO_SPEND_RATIO = {"hp": 0.5, "atk": 0.3, "def": 0.2, "regen": 0.0}

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PROGRESS.copy()

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)

def apply_auto_upgrades(progress):
    # Spend banked gold according to AUTO_SPEND_RATIO
    bank = progress["bank_gold"]
    if bank <= 0:
        return
    # Compute target buckets
    targets = {k: int(bank * r) for k, r in AUTO_SPEND_RATIO.items()}
    # Spend in round-robin order until gold exhausted or no purchases possible
    order = ["hp", "atk", "def", "regen"]
    while bank >= min(UPGRADE_COSTS.values()):
        purchase_made = False
        for stat in order:
            if targets[stat] < UPGRADE_COSTS[stat]:
                continue
            if bank >= UPGRADE_COSTS[stat]:
                bank -= UPGRADE_COSTS[stat]
                targets[stat] -= UPGRADE_COSTS[stat]
                progress["upgrades"][stat] += 1
                purchase_made = True
        if not purchase_made:
            break
    progress["bank_gold"] = bank

def derived_stats(progress):
    base = progress["base"]
    u = progress["upgrades"]
    max_hp = base["max_hp"] + u["hp"] * UPGRADE_EFFECT["hp"]
    atk = base["atk"] + u["atk"] * UPGRADE_EFFECT["atk"]
    df = base["def"] + u["def"] * UPGRADE_EFFECT["def"]
    regen = base["regen"] + u["regen"] * UPGRADE_EFFECT["regen"]
    return int(max_hp), int(atk), int(df), regen