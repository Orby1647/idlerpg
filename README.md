# 🧙‍♂️ Idle Roguelite

A terminal‑based auto‑dungeon crawler written in Python. The player explores procedurally generated floors, collects gold, fights monsters, and upgrades stats between runs — all rendered with colorful ANSI effects.

---

## ✨ Features

- Procedural dungeon generation  
- Auto‑movement using A* pathfinding  
- Turn‑based combat with crits, regen, and scaling  
- Fog of war (visible / explored / unseen tiles)  
- Colored terminal renderer (HUD, HP bar, flashing damage)  
- Multi‑line event log  
- Modular, readable codebase

---

## 🕹️ Run the Game

```bash
./main.sh
```

Requires **Python 3.10+**.

---

## 📁 Project Structure

```
src/
  main.py        # Entry point
  game.py        # Core logic & loop
  render.py      # Terminal rendering
  colors.py      # ANSI color constants
  progress.py    # Meta-progression

  dungeon/
    mapgen.py    # Procedural generation
    pathfinding.py
    constants.py
    entities.py
```

---

## 🛠️ Development

```bash
pytest
black src
ruff check src
```

---

## 📜 License

MIT License.
