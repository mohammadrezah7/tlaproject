# -*- coding: utf-8 -*-
"""
Glider-based Logic Gates Student Template Module.

"""
import numpy as np
from conway import GameOfLife


class GliderLogicGates:
    """
    Extension - Logic Gates.

    Signals are gliders travelling diagonally across a Game of Life grid:
    a glider present in a timing window is a '1' bit, its absence is '0'.
    Two gliders aimed at each other at a right angle can react in a few
    different ways depending on their exact relative offset and timing
    (phase): they can fully annihilate, pass through leaving debris, or -
    for a specific offset/phase combination - settle into a single,
    permanently stationary 2x2 "block" still life.

    The collision parameters used below (`_AND_*` / `_NOT_*`) were found
    by an exhaustive simulated search over relative row/column offsets and
    insertion-delay (phase) values using this same GameOfLife engine, and
    then verified against the full input truth table:
        AND: only (A=1, B=1) leaves a stable block at the output cell.
        NOT: input A present -> control glider is annihilated (output 0);
             input A absent  -> control glider survives untouched (output 1).
    """

    # The base glider shape used by GameOfLife.insertGlider() travels
    # diagonally down-and-right (south-east). The other three diagonal
    # headings are obtained by reflecting that shape.
    _BASE_GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    _SE = _BASE_GLIDER
    _SW = [(r, 2 - c) for r, c in _BASE_GLIDER]
    _NE = [(2 - r, c) for r, c in _BASE_GLIDER]
    _NW = [(2 - r, 2 - c) for r, c in _BASE_GLIDER]

    # --- AND gate collision (input A: SE, input B: SW) -----------------
    _AND_BASE = (12, 10)   # (row, col) start of the fixed input-A glider
    _AND_D = 2             # column separation of input-B's start from A's
    _AND_DROW = 1          # row offset of input-B's start relative to A's
    _AND_DELAY =   10       # generations to wait before spawning input-B
    _AND_TARGET = (15, 12)  # (row, col) top-left of the resulting 2x2 block
    _AND_STEPS = 60        # generations to run before reading the output

    # --- NOT gate collision (control: SE, input A: SW) ------------------
    _NOT_BASE = (5, 5)     # (row, col) start of the control glider
    _NOT_D = 2             # column separation of input-A's start from control's
    _NOT_DROW = 0          # row offset of input-A's start relative to control's
    _NOT_DELAY = 2         # generations to wait before spawning input A
    _NOT_STEPS = 60        # generations to run before reading the output

    @staticmethod
    def _place(life, offsets, index):
        """Stamp a set of (row, col) offsets as live cells at `index`."""
        for r, c in offsets:
            rr, cc = index[0] + r, index[1] + c
            if 0 <= rr < life.rows and 0 <= cc < life.cols:
                life.grid[rr, cc] = life.aliveValue

    @staticmethod
    def _is_block_at(grid, target):
        """True if exactly a 2x2 block of live cells sits at `target`."""
        tr, tc = target
        if tr + 1 >= grid.shape[0] or tc + 1 >= grid.shape[1]:
            return False
        region_alive = (
            grid[tr, tc] and grid[tr, tc + 1]
            and grid[tr + 1, tc] and grid[tr + 1, tc + 1]
        )
        return bool(region_alive) and int(grid.sum()) == 4

    def setup_and_gate(self, grid_size=35, input_a_present=False, input_b_present=False):
        """
        Set up the Game of Life grid for an AND gate.

        Args:
            grid_size (int): Size of the simulation grid.
            input_a_present (bool): If True, place glider for Input A.
            input_b_present (bool): If True, place glider for Input B.

        Returns:
            GameOfLife: Initialized GameOfLife object. A pending (delayed)
            insertion of input B - if requested - is stored on the object
            as `_pending_insert` for run_and_gate() to apply at the right
            generation, since input B must appear a few generations after
            input A for the collision to settle into a block.
        """
        life = GameOfLife(N=grid_size, finite=True, fastMode=True)
        life._pending_insert = None

        if input_a_present:
            self._place(life, self._SE, self._AND_BASE)

        if input_b_present:
            b_index = (self._AND_BASE[0] + self._AND_DROW, self._AND_BASE[1] + self._AND_D)
            life._pending_insert = (self._AND_DELAY, self._SW, b_index)

        return life

    def setup_not_gate(self, grid_size=35, input_a_present=False):
        """
        Set up the Game of Life grid for a NOT gate.

        Args:
            grid_size (int): Size of the simulation grid.
            input_a_present (bool): If True, place glider for Input A.

        Returns:
            GameOfLife: Initialized GameOfLife object, with the control
            glider always placed and a pending (delayed) insertion of
            input A - if requested - stored as `_pending_insert`.
        """
        life = GameOfLife(N=grid_size, finite=True, fastMode=True)
        life._pending_insert = None

        # The control glider always fires.
        self._place(life, self._SE, self._NOT_BASE)

        if input_a_present:
            a_index = (self._NOT_BASE[0] + self._NOT_DROW, self._NOT_BASE[1] + self._NOT_D)
            life._pending_insert = (self._NOT_DELAY, self._SW, a_index)

        return life

    def run_and_gate(self, input_a_present, input_b_present):
        """
        Run the AND gate simulation for a specific number of steps and return the output.

        Args:
            input_a_present (bool): Input A state.
            input_b_present (bool): Input B state.

        Returns:
            bool: True if output is active (a 2x2 block formed at the
            output cell - only possible when both inputs collide), False otherwise.
        """
        life = self.setup_and_gate(
            input_a_present=input_a_present, input_b_present=input_b_present
        )

        for generation in range(self._AND_STEPS):
            life.evolve()
            if life._pending_insert and generation + 1 == life._pending_insert[0]:
                _, offsets, index = life._pending_insert
                self._place(life, offsets, index)
                life._pending_insert = None

        return self._is_block_at(life.getStates(), self._AND_TARGET)

    def run_not_gate(self, input_a_present):
        """
        Run the NOT gate simulation for a specific number of steps and return the output.

        Args:
            input_a_present (bool): Input A state.

        Returns:
            bool: True if output is active (the control glider survives
            unimpeded), False otherwise (it was annihilated by input A).
        """
        life = self.setup_not_gate(input_a_present=input_a_present)

        for generation in range(self._NOT_STEPS):
            life.evolve()
            if life._pending_insert and generation + 1 == life._pending_insert[0]:
                _, offsets, index = life._pending_insert
                self._place(life, offsets, index)
                life._pending_insert = None

        # Output is "active" whenever anything is still alive: the only
        # way for the grid to be completely empty at this point is a full
        # glider-glider annihilation, which only happens when input A fired.
        return int(life.getStates().sum()) > 0
