import pytest
from typing import FrozenSet

from life import Grid, Game
from life.game_of_life import Cell


def test_grid_from_and_to_2d_list_empty():
    g = Grid.from_2d_list([])
    assert g.to_2d_list() == []
    assert isinstance(g.live, FrozenSet)
    assert len(g.live) == 0


def test_grid_immutable_live_cells():
    g = Grid([(0, 0), (0, 1)])
    with pytest.raises(AttributeError):
        g.live = set()  # Should not be able to assign to live property


def test_grid_from_and_to_2d_list_bounds():
    data = [
        [0, 1, 0],
        [1, 0, 0],
    ]
    g = Grid.from_2d_list(data)
    out = g.to_2d_list((0, 1, 0, 2))
    assert out == data


def test_block_stable():
    # 2x2 block should be stable
    data = [
        [1, 1],
        [1, 1],
    ]
    g = Grid.from_2d_list(data)
    game = Game(g)
    before = g.to_2d_list((0, 1, 0, 1))
    game.step()
    after = game.grid.to_2d_list((0, 1, 0, 1))
    assert before == after


def test_blinker_oscillates():
    # Vertical blinker
    data = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
    ]
    g = Grid.from_2d_list(data)
    game = Game(g)
    game.step()
    out = game.grid.to_2d_list((0, 2, 0, 2))
    expected = [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]
    assert out == expected


def test_glider_moves():
    # Classic glider: after 4 steps it should have moved down-right by 1
    glider = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    g = Grid.from_2d_list(glider)
    game = Game(g)
    game.run(4)
    out = game.grid.to_2d_list((1, 3, 1, 3))

    # expected: the original pattern shifted by (1,1)
    expected = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    assert out == expected


def test_step_idempotent_for_empty():
    g = Grid()
    game = Game(g)
    game.step()
    assert game.grid.to_2d_list() == []


def test_game_rules():
    # Test specific rule cases using apply_rules
    game = Game()
    
    # Test survival rules
    assert game.apply_rules((0, 0), count=1, is_alive=True) == False  # Dies (underpopulation)
    assert game.apply_rules((0, 0), count=2, is_alive=True) == True   # Survives
    assert game.apply_rules((0, 0), count=3, is_alive=True) == True   # Survives
    assert game.apply_rules((0, 0), count=4, is_alive=True) == False  # Dies (overpopulation)
    
    # Test birth rules
    assert game.apply_rules((0, 0), count=2, is_alive=False) == False  # Stays dead
    assert game.apply_rules((0, 0), count=3, is_alive=False) == True   # Born
    assert game.apply_rules((0, 0), count=4, is_alive=False) == False  # Stays dead


def test_neighbor_counting():
    # Test neighbor counting for a simple pattern
    game = Game()
    live_cells = frozenset([(0, 0), (0, 1), (1, 0)])  # L-shaped pattern
    counts = game.count_neighbors(live_cells)
    
    assert counts[(0, 0)] == 2  # Center cell has 2 neighbors
    assert counts[(1, 1)] == 3  # Empty cell with 3 neighbors
    assert (2, 2) not in counts  # Far cell not in counts since it has no neighbors