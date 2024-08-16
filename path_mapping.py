#Authored - Michael O'Donnell - 8/16/2024

import matplotlib.pyplot as plt
import numpy as np
import random

pattern = [
    "      ******************      ",
    "      ******************      ",
    "     ********************     ",
    "     ********************     ",
    "   ************************   ",
    "   ************************   ",
    " **************************** ",
    " **************************** ",
    " ************    ************ ",
    " ************    ************ ",
    " ************    ************ ",
    " ************    ************ ",
    " **************************** ",
    " **************************** ",
    "   ************************   ",
    "   ************************   ",
    "     ********************     ",
    "     ********************     ",
    "      ******************      ",
    "      ******************      "
]

#Channels that will highlighted
highlighted_channels = [(x, y) for x in range(21, 25) for y in range(2, 10)]

height = len(pattern)
width = len(pattern[0])

grid = np.zeros((height, width))

for y, row in enumerate(pattern):
    for x, char in enumerate(row):
        if char == '*':
            grid[y, x] = 1 

def is_highlighted_channel(x, y):
    return (x, y) in highlighted_channels

#such that the red line can be extended across un-highlighted channels
def extend_line(x1, y1, x2, y2, width, height):
    slope = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
    intercept = y1 - slope * x1
    
    if slope != float('inf'):
        x_left = 0
        y_left = slope * x_left + intercept
        
        x_right = width - 1
        y_right = slope * x_right + intercept
        
        y_top = 0
        x_top = (y_top - intercept) / slope
        
        y_bottom = height - 1
        x_bottom = (y_bottom - intercept) / slope
        
        points = [
            (x_left, y_left),
            (x_right, y_right),
            (x_top, y_top),
            (x_bottom, y_bottom)
        ]
        
        points = [(x, y) for x, y in points if 0 <= x < width and 0 <= y < height]
        
        return points[0], points[-1] 
        
    else:
        return (x1, 0), (x1, height - 1)

#Currently using randomly generated data. This function can be easily dealth with when dealing with root information. All you will have to do is
#take the root data and deal with it in the way which you would like, then send your parameters through the function.
def draw_lines(highlighted_channels, num_lines=1):
    for _ in range(num_lines):
        (x1, y1), (x2, y2) = random.sample(highlighted_channels, 2)

        square1_pos = (x1 - 0.15 + 0.15, y1 - 0.35 + 0.15)
        square2_pos = (x2 - 0.15 + 0.15, y2 - 0.35 + 0.15)

        square1 = square1_pos if random.choice([True, False]) else (x1 - 0.15 + 0.15, y1 + 0.05 + 0.15)
        square2 = square2_pos if random.choice([True, False]) else (x2 - 0.15 + 0.15, y2 + 0.05 + 0.15)
        
        start, end = extend_line(square1[0], square1[1], square2[0], square2[1], width, height)
        
        plt.plot([start[0], end[0]], [start[1], end[1]], color='red', linewidth=2)

fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.cm.gray
cmap.set_bad(color='white')

cax = ax.imshow(grid, cmap=cmap, interpolation='none')
plt.xticks(np.arange(width))
plt.yticks(np.arange(height))
plt.gca().invert_yaxis() 
plt.grid(False)

highlight_rect = plt.Rectangle((21 - 0.5, 2 - 0.5), 4, 8, linewidth=1, edgecolor='yellow', facecolor='yellow', alpha=0.5)
plt.gca().add_patch(highlight_rect)

for y in range(height):
    for x in range(width):
        if grid[y, x] == 1:
            rect = plt.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='none')
            plt.gca().add_patch(rect)
            
            if is_highlighted_channel(x, y):
                highlight_square = plt.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=2, edgecolor='none', facecolor='none')
                plt.gca().add_patch(highlight_square)
            
            small_square_1 = plt.Rectangle((x - 0.15, y - 0.35), 0.3, 0.3, linewidth=1, edgecolor='blue', facecolor='none')
            plt.gca().add_patch(small_square_1)
            
            small_square_2 = plt.Rectangle((x - 0.15, y + 0.05), 0.3, 0.3, linewidth=1, edgecolor='black', facecolor='none')
            plt.gca().add_patch(small_square_2)

draw_lines(highlighted_channels, num_lines=1)

plt.show()

#end
