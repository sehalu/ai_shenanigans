# Conway's Game of Life

A Python implementation of Conway's Game of Life with interactive visualizations.

## Features

- Sparse grid representation for efficient memory usage
- Interactive visualization with controls
- Multiple classic patterns included
- Cell age tracking and colorization
- Grid lines option
- Adjustable animation speed

## Installation

```bash
pip install -e .
```

For development, install with test dependencies:
```bash
pip install -e .[dev]
```

## Usage

### Basic Example
```python
from life import Grid, Game

# Create a glider
grid = Grid.from_2d_list([
    [0, 1, 0],
    [0, 0, 1],
    [1, 1, 1]
])
game = Game(grid)
game.run(4)  # Advance 4 steps
```

### Running Demos

Simple rainbow visualization:
```bash
python life/examples/simple.py
```

Interactive demo with controls:
```bash
python life/examples/interactive.py
```

The interactive demo includes:
- Play/Pause button
- FPS control (1-30 FPS)
- Grid lines toggle
- Pattern selector
- Population and age statistics

## Project Structure

```
life/
├── __init__.py
├── game_of_life.py     # Core implementation
└── examples/           # Visualization demos
    ├── __init__.py
    ├── simple.py       # Basic rainbow visualization
    └── interactive.py  # Full-featured interactive demo
```

## Development

Run tests:
```bash
pytest
```

## Performance

Memory usage is optimized through:
- Sparse grid representation (only live cells stored)
- Use of sets for O(1) lookups
- __slots__ for reduced memory footprint

Speed is optimized by:
- Efficient neighbor counting
- Minimal data structure overhead
- Cached computations where beneficial
