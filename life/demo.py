import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np
import time
from life.game_of_life import Grid, Game

def create_r_pentomino():
    """Create an R-pentomino pattern, known for chaotic growth."""
    return Grid.from_2d_list([
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0],
    ])

def create_rainbow_colormap():
    """Create a custom colormap: black for 0, rainbow colors for values > 0."""
    # Create rainbow colors for values > 0
    rainbow_colors = plt.cm.rainbow(np.linspace(0, 1, 256))
    
    # Create custom colormap with black (0, 0, 0) for value 0
    colors = np.vstack(([0, 0, 0, 1], rainbow_colors))
    
    # Create colormap that maps 0 to black and spreads rainbow colors across values > 0
    return mcolors.ListedColormap(colors)

def main():
    # Initialize the game with R-pentomino
    game = Game(create_r_pentomino())
    generation = 0
    
    # Create rainbow colormap
    cmap = create_rainbow_colormap()
    
    # Set up the plot with dark background
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#000000')
    ax.set_facecolor('#000000')
    plt.title("Conway's Game of Life - Rainbow Edition", color='white', pad=20)
    
    def update(frame):
        nonlocal generation
        # Clear the previous frame
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor('#000000')
        
        # Get current state and compute bounds
        if game.grid.live:
            rows, cols = zip(*game.grid.live)
            min_r, max_r = min(rows) - 1, max(rows) + 1
            min_c, max_c = min(cols) - 1, max(cols) + 1
        else:
            min_r = min_c = -10
            max_r = max_c = 10
        
        # Create the base grid array
        grid_array = np.zeros((max_r - min_r + 1, max_c - min_c + 1))
        
        # Assign rainbow values to live cells based on position
        for r, c in game.grid.live:
            # Use position to create a rainbow effect
            rainbow_val = ((r - min_r) / (max_r - min_r + 1) + 
                         (c - min_c) / (max_c - min_c + 1) + 
                         generation / 50) % 1
            grid_array[r - min_r, c - min_c] = rainbow_val * 0.8 + 0.2  # Scale to avoid pure black
        
        # Plot current state with rainbow colormap
        img = ax.imshow(grid_array, cmap=cmap, interpolation='nearest')
        ax.set_title(f'Generation {generation}', color='white', pad=20)
        
        # Advance to next state
        game.step()
        generation += 1
        
        # Add a small delay to achieve approximately 10 FPS
        time.sleep(0.1)  # 0.1 seconds = 10 FPS
        
        return [img]

    # Create and run the animation
    ani = animation.FuncAnimation(
        fig, update, frames=200, 
        interval=1, blit=True
    )
    
    plt.show()

if __name__ == "__main__":
    main()