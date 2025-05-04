# River Ride (Terminal Game)

A terminal-based action game inspired by the classic *River Raid*. Navigate your ship through a narrowing river, avoid enemies and shoot them, collect fuel in your way. All inside your terminal window using Python and `curses`!

- Use **W A S D** to move:
  - `W` – move up
  - `S` – move down
  - `A` – move left
  - `D` – move right
- Press `SPACE` to shoot bullets upward
- Press `Q` to quit the game

Avoid crashing into the riverbanks (green blocks) or enemies (`E`). Collect fuel (`$`) to stay alive. Your fuel gradually decreases over time. Shoot enemies to gain score!

## 🛠 Requirements

- Python 3.6+
- `curses` module (pre-installed on Linux/macOS, for Windows use Windows Terminal or install via [`windows-curses`](https://pypi.org/project/windows-curses/))

```bash
pip install windows-curses  # Only for Windows
