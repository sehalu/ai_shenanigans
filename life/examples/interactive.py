"""Interactive visualization of Conway's Game of Life with controls and patterns."""
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, RadioButtons, CheckButtons
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np
import time
from life.game_of_life import Grid, Game
from typing import Dict, List, Set

# Common patterns used in Game of Life
PATTERNS = {
    'R-pentomino': [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0],
    ],
    'Glider': [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ],
    'Pulsar': [
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,0,0,1,1,1,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,1,1,1,0,0,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
    ],
    'Gosper Glider Gun': [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ],
    'Pentadecathlon': [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,1,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,1,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
    ],
    'Random': None
}


class GameOfLifeDemo:
    """Interactive demo of Conway's Game of Life with visualization controls."""
    
    def __init__(self):
        self.cell_ages = {}  # Track age of each cell
        self.max_age = 50  # Maximum age for color scaling
        self.patterns = PATTERNS
        
        self.setup_ui()
        self.paused = False
        self.fps = 10
        self.generation = 0
        
    def create_random_pattern(self, size=30, density=0.3):
        """Create a random pattern with given size and density."""
        pattern = np.random.choice([0, 1], size=(size, size), p=[1-density, density])
        return pattern.tolist()
        
    def setup_ui(self):
        """Initialize the user interface with controls."""
        # Create figure with space for controls
        self.fig = plt.figure(figsize=(12, 10))
        self.fig.patch.set_facecolor('#000000')
        
        # Main plot
        self.ax_main = self.fig.add_axes([0.1, 0.25, 0.8, 0.65])
        self.ax_main.set_facecolor('#000000')
        
        # Control buttons
        ax_playpause = self.fig.add_axes([0.1, 0.1, 0.1, 0.04])
        self.btn_playpause = Button(ax_playpause, 'Pause', color='lightgray')
        self.btn_playpause.on_clicked(self.toggle_pause)
        
        # Speed slider
        ax_speed = self.fig.add_axes([0.25, 0.1, 0.2, 0.04])
        self.slider_speed = Slider(ax_speed, 'FPS', 1, 30, valinit=10)
        self.slider_speed.on_changed(self.update_speed)
        
        # Grid lines toggle
        ax_grid = self.fig.add_axes([0.5, 0.1, 0.15, 0.04])
        self.check_grid = CheckButtons(ax_grid, ['Grid'], [True])
        self.check_grid.on_clicked(self.toggle_grid)
        
        # Pattern selector
        ax_patterns = self.fig.add_axes([0.7, 0.02, 0.2, 0.15])
        self.radio_patterns = RadioButtons(ax_patterns, list(self.patterns.keys()))
        self.radio_patterns.on_clicked(self.change_pattern)
        
        # Initialize game
        self.change_pattern('R-pentomino')
        
        # Setup rainbow colormap
        rainbow_colors = plt.cm.rainbow(np.linspace(0, 1, 256))
        colors = np.vstack(([0, 0, 0, 1], rainbow_colors))
        self.cmap = mcolors.ListedColormap(colors)
        
    def toggle_pause(self, event):
        """Pause or resume the animation."""
        self.paused = not self.paused
        self.btn_playpause.label.set_text('Resume' if self.paused else 'Pause')
        
    def update_speed(self, val):
        """Update animation speed."""
        self.fps = val

    def toggle_grid(self, label):
        """Toggle grid lines on/off."""
        self.ax_main.grid(self.check_grid.get_status()[0], color='gray', alpha=0.3)
        
    def change_pattern(self, label):
        """Switch to a different initial pattern."""
        if label == 'Random':
            pattern = self.create_random_pattern()
        else:
            pattern = self.patterns[label]
        self.game = Game(Grid.from_2d_list(pattern))
        self.generation = 0
        self.cell_ages.clear()
        
    def update_cell_ages(self):
        """Update the age of each cell."""
        current_cells = set(self.game.grid.live)
        
        # Age existing cells
        self.cell_ages = {cell: age + 1 for cell, age in self.cell_ages.items() if cell in current_cells}
        
        # Add new cells
        new_cells = current_cells - set(self.cell_ages.keys())
        for cell in new_cells:
            self.cell_ages[cell] = 0
        
    def update(self, frame):
        """Update the animation frame."""
        if self.paused:
            return []
            
        self.ax_main.clear()
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_facecolor('#000000')
        
        # Restore grid state
        self.ax_main.grid(self.check_grid.get_status()[0], color='gray', alpha=0.3)
        
        if self.game.grid.live:
            rows, cols = zip(*self.game.grid.live)
            min_r, max_r = min(rows) - 1, max(rows) + 1
            min_c, max_c = min(cols) - 1, max(cols) + 1
        else:
            min_r = min_c = -10
            max_r = max_c = 10
            
        grid_array = np.zeros((max_r - min_r + 1, max_c - min_c + 1))
        
        # Update cell ages and colors
        self.update_cell_ages()
        
        # Update live cells with age-based colors
        for r, c in self.game.grid.live:
            # Color based on cell age and position
            age_factor = min(self.cell_ages[(r, c)] / self.max_age, 1.0)
            pos_factor = ((r - min_r) / (max_r - min_r + 1) + 
                        (c - min_c) / (max_c - min_c + 1)) % 1
            
            # Combine age and position for final color
            rainbow_val = (age_factor * 0.5 + pos_factor * 0.5) % 1
            grid_array[r - min_r, c - min_c] = rainbow_val * 0.8 + 0.2
            
        img = self.ax_main.imshow(grid_array, cmap=self.cmap, interpolation='nearest')
        
        # Add statistics
        stats = (f'Generation: {self.generation} | '
                f'Population: {len(self.game.grid.live)} | '
                f'Oldest Cell: {max(self.cell_ages.values()) if self.cell_ages else 0}')
        self.ax_main.set_title(stats, color='white', pad=20)
        
        if not self.paused:
            self.game.step()
            self.generation += 1
            
        time.sleep(1/self.fps)
        return [img]
        
    def run(self):
        """Start the animation."""
        self.ani = animation.FuncAnimation(
            self.fig, self.update, frames=None,
            interval=1, blit=True
        )
        plt.show()


def main():
    """Run the interactive demo."""
    demo = GameOfLifeDemo()
    demo.run()


if __name__ == "__main__":
    main()