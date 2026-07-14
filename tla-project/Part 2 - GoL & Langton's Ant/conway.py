import numpy as np
from scipy import signal, ndimage


def _parse_plaintext(lines):
    pattern_lines = []
    for line in lines:
        if not line.startswith('!'):
            pattern_lines.append(line)

    while pattern_lines and pattern_lines[-1] == '':
        pattern_lines.pop()

    live_cells = []
    height = len(pattern_lines)
    width = 0

    for line in pattern_lines:
        if len(line) > width:
            width = len(line)

    for r, line in enumerate(pattern_lines):
        for c, ch in enumerate(line):
            if ch in ('O', 'o'):
                live_cells.append((r, c))

    return width, height, live_cells


def _parse_rle(lines):
    width = height = 0
    body_lines = []

    for line in lines:
        if not line or line.startswith('#'):
            continue
        if line.lower().startswith('x'):
            for token in line.split(','):
                token = token.strip()
                if token.lower().startswith('x'):
                    width = int(token.split('=')[1].strip())
                elif token.lower().startswith('y'):
                    height = int(token.split('=')[1].strip())
            continue
        body_lines.append(line)

    body = ''.join(body_lines)
    body = body.split('!')[0]

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

    if not width:
        max_col = -1

        for row, col in live_cells:
            if col > max_col:
                max_col = col

        width = max_col + 1

    if not height:
        max_row = -1

        for row, col in live_cells:
            if row > max_row:
                max_row = row

        height = max_row + 1

    return width, height, live_cells


def parse_pattern(filepath):

    with open(filepath, 'r') as f:
        raw_lines = f.readlines()

    
    lines = [line.rstrip('\r\n') for line in raw_lines]

    is_rle = filepath.lower().endswith('.rle')
    if not is_rle:
        
        for line in lines:
            if line.startswith('!') or line.strip() == '':
                continue
            is_rle = line.lower().startswith('x')
            break

    if is_rle:
        return _parse_rle(lines)
    return _parse_plaintext(lines)

class GameOfLife:

    def __init__(self, N=256, finite=False, fastMode=True):
        self.grid = np.zeros((N, N), np.uint)
        self.neighborhood = np.ones((3, 3), np.uint)
        self.neighborhood[1, 1] = 0  
        self.finite = finite
        self.fastMode = fastMode
        self.aliveValue = 1
        self.deadValue = 0
        self.rows = N 
        self.cols = N  

    def getStates(self):
        return self.grid

    def getGrid(self):
        return self.getStates()

    def update_grid_fast(self, grid):
        
        boundary = 'fill'
        if not self.finite:
            boundary = 'wrap'

        neighbor_count = signal.convolve2d(
            grid,
            self.neighborhood,
            mode='same',
            boundary=boundary,
            fillvalue=0
)

        new_grid = np.zeros_like(grid)

        rows = len(grid)
        cols = len(grid[0])

        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == self.aliveValue:
                    if neighbor_count[i][j] == 2 or neighbor_count[i][j] == 3:
                        new_grid[i][j] = self.aliveValue

                else:
                    if neighbor_count[i][j] == 3:
                        new_grid[i][j] = self.aliveValue

        return new_grid

    def evolve(self):
        if self.fastMode:
            self.grid = self.update_grid_fast(self.grid)
        else:
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
                                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                    live_neighbors += self.grid[rr, cc]
                            else:
                                
                                rr %= self.rows
                                cc %= self.cols
                                live_neighbors += self.grid[rr, cc]

                    if self.grid[r, c] == self.aliveValue:
                        
                        if live_neighbors in (2, 3):
                            new_grid[r, c] = self.aliveValue
                        else:
                            new_grid[r, c] = self.deadValue
                    else:
                        if live_neighbors == 3:
                            new_grid[r, c] = self.aliveValue
                        else:
                            new_grid[r, c] = self.deadValue

            self.grid = new_grid

    def insertBlinker(self, index=(0, 0)):
        self.grid[index[0], index[1] + 1] = self.aliveValue
        self.grid[index[0] + 1, index[1] + 1] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 1] = self.aliveValue

    def insertGlider(self, index=(0, 0)):
        self.grid[index[0], index[1] + 1] = self.aliveValue
        self.grid[index[0] + 1, index[1] + 2] = self.aliveValue
        self.grid[index[0] + 2, index[1]] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 1] = self.aliveValue
        self.grid[index[0] + 2, index[1] + 2] = self.aliveValue

    def insertGliderGun(self, index=(0, 0)):

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
        width, height, live_cells = parse_pattern(filename)
        for r, c in live_cells:
            target_r = index[0] + r
            target_c = index[1] + c
            if 0 <= target_r < self.rows and 0 <= target_c < self.cols:
                self.grid[target_r, target_c] = self.aliveValue