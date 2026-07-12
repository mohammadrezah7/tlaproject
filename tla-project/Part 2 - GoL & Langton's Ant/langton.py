# -*- coding: utf-8 -*-
"""
Langton's Ant Student Template Module.
"""
import numpy as np


class LangtonsAnt:
    """
    Langton's Ant cellular automaton.

    The ant walks a toroidal NxN grid. Each cell holds a "color" (an
    integer state, 0 = white by default). At every step the ant:
        1. Reads the color of the cell it stands on.
        2. Looks up (next_color, turn_direction) for that color in `rules`.
        3. Repaints the cell with next_color.
        4. Turns clockwise ('R') or counter-clockwise ('L') from its
           current heading.
        5. Moves forward one cell in its new heading direction, wrapping
           around the grid edges (toroidal boundary).

    With the classic 2-color ruleset {0: (1, 'R'), 1: (0, 'L')} this
    reproduces the standard Langton's Ant rule:
        - On a white (0) square: flip it to black (1), turn right, move.
        - On a black (1) square: flip it to white (0), turn left, move.

    Supplying a longer `rules` dictionary (e.g. cycling through colors
    0 -> 1 -> 2 -> 3 -> 0 with a mix of 'R'/'L' turns, as in the
    "RLR"/"LLRR"-style rulesets) generalizes the ant to multi-color
    behaviour without any change to the stepping logic below.
    """

    # Compass directions in clockwise order: Up, Right, Down, Left.
    _DIRECTIONS = ('U', 'R', 'D', 'L')
    # Row/column deltas for each heading (row grows downward, like the grid).
    _DIRECTION_DELTAS = {
        'U': (-1, 0),
        'R': (0, 1),
        'D': (1, 0),
        'L': (0, -1),
    }

    def __init__(self, N, ant_position, rules):
        """
        Initialize the Langton's Ant simulation.

        Args:
            N (int): The grid size (NxN).
            ant_position (tuple): Starting coordinate of the ant as (r, c).
            rules (dict): Dictionary defining transition rules.
                          Format: {current_color: (next_color, turn_direction)}
        """
        self.N = N
        self.grid = np.zeros((N, N), dtype=int)
        self.position = [ant_position[0] % N, ant_position[1] % N]
        self.rules = rules
        # The ant starts facing "Up" (north), the first of the URDL headings.
        self.direction_index = 0

    def get_states(self):
        """
        Returns the current state grid of the cells.

        Returns:
            np.ndarray: The NxN cellular grid.
        """
        return self.grid

    def get_current_position(self):
        """
        Returns the ant's current position as a tuple (r, c).

        Returns:
            tuple: Current coordinates of the ant.
        """
        return tuple(self.position)

    def step(self):
        """
        Perform a single simulation step following the ruleset.
        """
        r, c = self.position
        current_color = int(self.grid[r, c])

        next_color, turn_direction = self.rules[current_color]

        # 1. Repaint the current cell.
        self.grid[r, c] = next_color

        # 2. Turn clockwise ('R') or counter-clockwise ('L').
        if turn_direction == 'R':
            self.direction_index = (self.direction_index + 1) % 4
        elif turn_direction == 'L':
            self.direction_index = (self.direction_index - 1) % 4
        else:
            raise ValueError(
                f"Unknown turn direction {turn_direction!r}; expected 'R' or 'L'."
            )

        # 3. Move forward one cell in the (new) heading, wrapping toroidally.
        heading = self._DIRECTIONS[self.direction_index]
        dr, dc = self._DIRECTION_DELTAS[heading]
        self.position = [(r + dr) % self.N, (c + dc) % self.N]

    def update(self):
        """
        Alias for step() to support standard animation.
        """
        self.step()
