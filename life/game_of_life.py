from typing import Iterable, Set, Tuple, List, FrozenSet

Cell = Tuple[int, int]


class Grid:
    """Sparse representation of an infinite grid using a set of live cell coordinates.

    Stores only live cells as tuples (row, col). Provides helpers to
    construct from 2D lists and to export a bounded 2D list.
    """
    
    __slots__ = ('_live',)

    def __init__(self, live: Iterable[Cell] = ()):  # pragma: no cover - trivial
        self._live: Set[Cell] = set(live)

    @property
    def live(self) -> FrozenSet[Cell]:
        """Get the immutable set of live cells."""
        return frozenset(self._live)

    @classmethod
    def from_2d_list(cls, data: List[List[int]]) -> "Grid":
        live = set()
        for r, row in enumerate(data):
            for c, v in enumerate(row):
                if v:
                    live.add((r, c))
        return cls(live)

    def to_2d_list(self, bounds: Tuple[int, int, int, int] = None) -> List[List[int]]:
        """Return a 2D list representation.

        Args:
            bounds: (min_r, max_r, min_c, max_c). If None, compute tight bounds around live cells.
        
        Returns:
            List[List[int]]: 2D grid with 1 for live cells, 0 for dead cells
        """
        live_cells: FrozenSet[Cell] = self.live
        
        if not live_cells:
            if bounds is None:
                return []
            width: int = bounds[3] - bounds[2] + 1
            height: int = bounds[1] - bounds[0] + 1
            return [[0] * width for _ in range(height)]

        if bounds is None:
            rows: List[int] = [r for r, _ in live_cells]
            cols: List[int] = [c for _, c in live_cells]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)
        else:
            min_r, max_r, min_c, max_c = bounds

        out = []
        for r in range(min_r, max_r + 1):
            row = []
            for c in range(min_c, max_c + 1):
                row.append(1 if (r, c) in self.live else 0)
            out.append(row)
        return out

    def __contains__(self, cell: Cell) -> bool:
        return cell in self.live

    def copy(self) -> "Grid":
        return Grid(set(self.live))


class Game:
    """Encapsulates Game of Life rules and iteration.

    Uses Conway's rules:
      - Any live cell with 2 or 3 live neighbours survives.
      - Any dead cell with exactly 3 live neighbours becomes a live cell.
      - All other live cells die in the next generation. Similarly, all other dead cells stay dead.
    """
    
    __slots__ = ('_grid', '_bounds_cache')

    SURVIVE_MIN: int = 2
    SURVIVE_MAX: int = 3
    BIRTH_COUNT: int = 3
    
    NEIGHBORS: FrozenSet[Cell] = frozenset([
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ])

    def __init__(self, grid: Grid = None):
        self._grid = grid or Grid()
        self._bounds_cache: Tuple[int, int, int, int] | None = None

    @property
    def grid(self) -> Grid:
        """Get the current grid state."""
        return self._grid

    def count_neighbors(self, live_cells: FrozenSet[Cell]) -> dict[Cell, int]:
        """Count neighbors for all cells adjacent to live cells."""
        neighbor_counts: dict[Cell, int] = {}
        
        for (r, c) in live_cells:
            # ensure cell is in dict so we can process live cells with zero neighbors
            neighbor_counts.setdefault((r, c), 0)
            for dr, dc in Game.NEIGHBORS:
                nbr = (r + dr, c + dc)
                neighbor_counts[nbr] = neighbor_counts.get(nbr, 0) + 1
                
        return neighbor_counts

    def apply_rules(self, cell: Cell, count: int, is_alive: bool) -> bool:
        """Apply Conway's rules to determine if a cell lives or dies."""
        if is_alive:
            return Game.SURVIVE_MIN <= count <= Game.SURVIVE_MAX
        return count == Game.BIRTH_COUNT

    def step(self) -> Grid:
        """Advance the game by one generation and return the new Grid."""
        live_cells = self.grid.live
        neighbor_counts = self.count_neighbors(live_cells)

        new_live = {
            cell for cell, count in neighbor_counts.items()
            if self.apply_rules(cell, count, cell in live_cells)
        }

        self._grid = Grid(new_live)
        self._bounds_cache = None  # Invalidate bounds cache
        return self.grid

    def run(self, steps: int) -> Grid:
        """Run the game for given number of steps and return final Grid."""
        for _ in range(steps):
            self.step()
        return self.grid
