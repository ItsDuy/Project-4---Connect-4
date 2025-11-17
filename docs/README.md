## Members:
Nguyễn Anh Duy

Phạm Quang Anh Duy

Nguyễn Quốc Hiệu

Cao Quế Phương

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
Start a server:
```
python .\server.py
```
Start from the main menu (recommended):
Each player:
```powershell
python .\main.py
```
The second player does the same thing.
One of the player will host room and the second one would type in the room's code to join.
When both players are ready the game will start.


## Controls

- Mouse: click a column to drop a piece
- R: restart after game over
- Esc or Q: quit

### Main Menu

- Play PvP: start a two-player local match.
- Play AI: Three differant modes: easy-medium-hard using mini-max pruning stratgety with orders_moves_by_heuristic (prefer middle column)
- AI vs AI: Watch different AI modes combat each other.
- Music Settings: adjust BGM/SFX volumes; press Esc/Backspace to go back
