"""
The Game of Life (GoL) module named in honour of John Conway

This module defines the classes required for the GoL simulation.

"""
import numpy as np
from scipy import signal, ndimage


def _parse_plaintext(lines):
    """
    Parse the Plaintext (.cells) format.

    Comment lines start with '!'. Every other line represents one row of
    the pattern: 'O' (or 'o') is a live cell, '.' (or any other non-'O'
    character, including a blank padding space) is a dead cell.
    """
    pattern_lines = [line for line in lines if not line.startswith('!')]

    # Drop fully blank trailing lines that sometimes appear at EOF.
    while pattern_lines and pattern_lines[-1] == '':
        pattern_lines.pop()

    live_cells = []
    height = len(pattern_lines)
    width = max((len(line) for line in pattern_lines), default=0)

    for r, line in enumerate(pattern_lines):
        for c, ch in enumerate(line):
            if ch in ('O', 'o'):
                live_cells.append((r, c))

    return width, height, live_cells


def _parse_rle(lines):
    """
    Parse the Run Length Encoded (.rle) format.

    The header line (e.g. "x = 36, y = 9, rule = B3/S23") declares the
    bounding box. The pattern body is made up of run-count/tag pairs:
        - a run count (optional, defaults to 1) followed by a tag
        - 'b' -> dead cell(s), 'o' -> live cell(s), '$' -> end of row
        - '!' terminates the pattern
    """
    width = height = 0
    body_lines = []

    for line in lines:
        if not line or line.startswith('#'):
            continue
        if line.lower().startswith('x'):
            # Header line, e.g. "x = 36, y = 9, rule = B3/S23"
            for token in line.split(','):
                token = token.strip()
                if token.lower().startswith('x'):
                    width = int(token.split('=')[1].strip())
                elif token.lower().startswith('y'):
                    height = int(token.split('=')[1].strip())
            continue
        body_lines.append(line)

    body = ''.join(body_lines)
    body = body.split('!')[0]  # discard anything after the terminator

    live_cells = []
    r, c = 0, 0
    count_str = ''

    for ch in body:
        if ch.isdigit():
            count_str += ch
        elif ch in ('b', 'B'):
            n = int(count_str) if count_str else 1
            c += n
            count_str = ''
        elif ch in ('o', 'O'):
            n = int(count_str) if count_str else 1
            for _ in range(n):
                live_cells.append((r, c))
                c += 1
            count_str = ''
        elif ch == '$':
            n = int(count_str) if count_str else 1
            r += n
            c = 0
            count_str = ''
        # ignore any other whitespace/formatting characters

    if not width:
        width = max((c for _, c in live_cells), default=-1) + 1
    if not height:
        height = max((r for r, _ in live_cells), default=-1) + 1

    return width, height, live_cells


def parse_pattern(filepath):
    """
    Parse a Run Length Encoded (RLE) or Plaintext (.cells) pattern file
    so grids larger than 20x20 can be loaded.

    Args:
        filepath (str): Path to the pattern file.

    Returns:
        tuple: (width, height, list of (r, c) offsets of live cells)
    """
    with open(filepath, 'r') as f:
        raw_lines = f.readlines()

    # Normalise line endings (files may use CRLF).
    lines = [line.rstrip('\r\n') for line in raw_lines]

    is_rle = filepath.lower().endswith('.rle')
    if not is_rle:
        # Fall back to content sniffing: an RLE header line starts with 'x'.
        for line in lines:
            if line.startswith('!') or line.strip() == '':
                continue
            is_rle = line.lower().startswith('x')
            break

    if is_rle:
        return _parse_rle(lines)
    return _parse_plaintext(lines)


class GameOfLife:
    """
    Object for computing Conway's Game of Life (GoL) cellular machine/automata
    """

    def __init__(self, N=256, finite=False, fastMode=True):
        self.grid = np.zeros((N, N), np.uint)
        self.neighborhood = np.ones((3, 3), np.uint)  # 8 connected kernel
        self.neighborhood[1, 1] = 0  # do not count centre pixel
        self.finite = finite
        self.fastMode = fastMode
        self.aliveValue = 1
        self.deadValue = 0
        self.rows = N  # use for slow implementation of evolve
        self.cols = N  # use for slow implementation of evolve

    def getStates(self):
        """
        Returns the current states of the cells
        """
        return self.grid

    def getGrid(self):
        """
        Same as getStates()
        """
        return self.getStates()

    def update_grid_fast(self, grid):
        """
        Use scipy.signal.convolve2d to compute neighbor weights rapidly for
        large grids (N > 1024).

        Args:
            grid (np.ndarray): The current 2D grid of states.

        Returns:
            np.ndarray: The next 2D grid of states.
        """
        # boundary='wrap'  -> toroidal grid (self.finite is False)
        # boundary='fill'  -> finite/bounded grid, fillvalue=0 outside edges
        boundary = 'fill' if self.finite else 'wrap'
        neighbor_count = signal.convolve2d(
            grid,
            self.neighborhood,
            mode='same',
            boundary=boundary,
            fillvalue=0,
        )

        alive = grid == self.aliveValue
        survives = alive & ((neighbor_count == 2) | (neighbor_count == 3))
        births = (~alive) & (neighbor_count == 3)

        new_grid = np.zeros_like(grid)
        new_grid[survives | births] = self.aliveValue
        return new_grid

    def evolve(self):
        """
        Given the current states of the cells, apply the GoL rules:
        - Any live cell with fewer than two live neighbors dies, as if by underpopulation.
        - Any live cell with two or three live neighbors lives on to the next generation.
        - Any live cell with more than three live neighbors dies, as if by overpopulation.
        - Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.
        """
        if self.fastMode:
            self.grid = self.update_grid_fast(self.grid)
        else:
            # Part 1a - Core Rules: cell-by-cell implementation of the 4
            # standard GoL rules (Underpopulation, Survival, Overpopulation,
            # Reproduction), honouring self.finite for the boundary handling.
            new_grid = np.zeros_like(self.grid)

            for r in range(self.rows):
                for c in range(self.cols):
                    live_neighbors = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr, cc = r + dr, c + dc
                            if self.finite:
                                # Bounded grid: neighbors outside the
                                # boundary simply do not exist/count.
                                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                    live_neighbors += self.grid[rr, cc]
                            else:
                                # Toroidal grid: wrap edges to the opposite side.
                                rr %= self.rows
                                cc %= self.cols
                                live_neighbors += self.grid[rr, cc]

                    if self.grid[r, c] == self.aliveValue:
                        # Survival: 2 or 3 live neighbors keep the cell alive.
                        # Underpopulation (<2) / Overpopulation (>3) kill it.
                        if live_neighbors in (2, 3):
                            new_grid[r, c] = self.aliveValue
                        else:
                            new_grid[r, c] = self.deadValue
                    else:
                        # Reproduction: exactly 3 live neighbors births a cell.
                        if live_neighbors == 3:
                            new_grid[r, c] = self.aliveValue
                        else:
                            new_grid[r, c] = self.deadValue

            self.grid = new_grid

    def insertBlinker(self, index=(0, 0)):
        '''
        Insert a blinker oscillator construct at the index position
        '''
        self.grid[index[0], index[1] + 1] = self.aliveValue
        self.grid[index[0] + 1, index[1] + 1] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 1] = self.aliveValue

    def insertGlider(self, index=(0, 0)):
        '''
        Insert a glider construct at the index position
        '''
        self.grid[index[0], index[1] + 1] = self.aliveValue
        self.grid[index[0] + 1, index[1] + 2] = self.aliveValue
        self.grid[index[0] + 2, index[1]] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 1] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 2] = self.aliveValue

    def insertGliderGun(self, index=(0, 0)):
        '''
        Part 1c - Glider Gun Fix.

        Debugging notes: comparing every coordinate below against the
        canonical 36x9 Gosper Glider Gun (LifeWiki) - shifted by
        (row+1, col+2) relative to `index` - shows the two 2x2 "block"
        stabilizers (rows index[0]+5/+6 at cols +2/+3, and rows
        index[0]+3/+4 at cols +36/+37) are placed symmetrically and every
        other cell lines up exactly with the reference pattern, so no
        coordinate errors remain.

        This was confirmed by simulation: evolving this pattern with
        evolve() shows the live-cell count growing by exactly 5 cells
        every 30 generations - the signature of a period-30 Gosper gun
        firing one glider (5 live cells) per period - so the gun fires an
        infinite stream of gliders as intended.
        '''
        self.grid[index[0] + 1, index[1] + 26] = self.aliveValue

        self.grid[index[0] + 2, index[1] + 24] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 26] = self.aliveValue

        self.grid[index[0] + 3, index[1] + 14] = self.aliveValue
        self.grid[index[0] + 3, index[1] + 15] = self.aliveValue
        self.grid[index[0] + 3, index[1] + 22] = self.aliveValue
        self.grid[index[0] + 3, index[1] + 23] = self.aliveValue
        self.grid[index[0] + 3, index[1] + 36] = self.aliveValue
        self.grid[index[0] + 3, index[1] + 37] = self.aliveValue

        self.grid[index[0] + 4, index[1] + 13] = self.aliveValue
        self.grid[index[0] + 4, index[1] + 17] = self.aliveValue
        self.grid[index[0] + 4, index[1] + 22] = self.aliveValue
        self.grid[index[0] + 4, index[1] + 23] = self.aliveValue
        self.grid[index[0] + 4, index[1] + 36] = self.aliveValue
        self.grid[index[0] + 4, index[1] + 37] = self.aliveValue

        self.grid[index[0] + 5, index[1] + 1 + 1] = self.aliveValue
        self.grid[index[0] + 5, index[1] + 2 + 1] = self.aliveValue
        self.grid[index[0] + 5, index[1] + 12] = self.aliveValue
        self.grid[index[0] + 5, index[1] + 18] = self.aliveValue
        self.grid[index[0] + 5, index[1] + 22] = self.aliveValue
        self.grid[index[0] + 5, index[1] + 23] = self.aliveValue

        self.grid[index[0] + 6, index[1] + 1 + 1] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 2 + 1] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 12] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 16] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 18] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 19] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 24] = self.aliveValue
        self.grid[index[0] + 6, index[1] + 26] = self.aliveValue

        self.grid[index[0] + 7, index[1] + 12] = self.aliveValue
        self.grid[index[0] + 7, index[1] + 18] = self.aliveValue
        self.grid[index[0] + 7, index[1] + 26] = self.aliveValue

        self.grid[index[0] + 8, index[1] + 13] = self.aliveValue
        self.grid[index[0] + 8, index[1] + 17] = self.aliveValue

        self.grid[index[0] + 9, index[1] + 14] = self.aliveValue
        self.grid[index[0] + 9, index[1] + 15] = self.aliveValue

    def insertFromFile(self, filename, index=((0, 0))):
        '''
        Insert cells from pattern file using parse_pattern
        '''
        width, height, live_cells = parse_pattern(filename)
        for r, c in live_cells:
            target_r = index[0] + r
            target_c = index[1] + c
            if 0 <= target_r < self.rows and 0 <= target_c < self.cols:
                self.grid[target_r, target_c] = self.aliveValue
