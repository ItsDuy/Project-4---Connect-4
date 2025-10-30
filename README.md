# Connect 4 (Python + Pygame)

A simple two-player Connect Four game implemented with Python and Pygame. Click a column to drop your piece. First to connect four horizontally, vertically, or diagonally wins.

## Features

- Clean, modern board rendering
- Two-player local play (Red vs Yellow)
- Win and draw detection
- Press R to restart after a game; Esc or Q to quit
- Optional `--test` flag to run quick logic self-tests (no window)

## Requirements

- Python 3.8+
- Pygame

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run

Start from the main menu (recommended):

```powershell
python .\MainScreen.py
```

Start the game directly (skips menu):

```powershell
python .\ConnectFour.py
```

Run logic self-tests (no GUI):

```powershell
python .\ConnectFour.py --test
```

## Controls

- Mouse: click a column to drop a piece
- R: restart after game over
- Esc or Q: quit

### Main Menu

- Play PvP: start a two-player local match
- Play AI: placeholder (coming soon)
- Music Settings: adjust BGM/SFX volumes; press Esc/Backspace to go back

## Notes

- Window size is 700x700 pixels by default. You can adjust `cell_size` or other constants in `ConnectFour` to change appearance.
- The main menu uses a background image from `assets/bg.jpeg` if present; otherwise, a solid background is shown.