# Block Puzzle Game

A Pygame-based block puzzle game with advanced features including:
- 6x6 Grid gameplay
- Draggable block placement
- Automatic row and column clearing
- Score tracking with combo multipliers
- Multiple block shapes (single, double, triple, L-shape, square, T-shape, Z-shape)
- Next block preview

## Requirements

- Python 3.13 (pygame wheels are not yet available for Python 3.14)
- pygame 2.6.1

## Installation

```bash
py -3.13 -m pip install -r requirements.txt
```

## Running the Game

### Option 1: Batch File (Windows)
Double-click `run.bat`

### Option 2: Command Line
```bash
py -3.13 main.py
```

## Controls

- **Click and Drag**: Place blocks on the grid
- **R Key**: Rotate current block
- **ESC Key**: Exit game

## Gameplay

1. Drag and drop blocks from the preview onto the grid
2. Fill complete rows or columns to clear them
3. Build combos by clearing multiple lines consecutively
4. Game ends when no more blocks can be placed
5. Score increases with each block placed and bonus points for clearing lines
