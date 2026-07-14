
import numpy as np
from conway import GameOfLife


class GliderLogicGates:

    _BASE_GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    _SE = _BASE_GLIDER
    _SW = []
    _NE = []
    _NW = []
    for i in range(len(_BASE_GLIDER)):
        _SW.append((_BASE_GLIDER[i][0],2-_BASE_GLIDER[i][1]))
        _NE.append((2-_BASE_GLIDER[i][0],_BASE_GLIDER[i][1]))
        _NW.append((2-_BASE_GLIDER[i][0],2-_BASE_GLIDER[i][1]))
        
   
    _AND_BASE = (12, 10)   
    _AND_D = 2             
    _AND_DROW = 1          
    _AND_DELAY =   3      
    _AND_TARGET = (15, 12)  
    _AND_STEPS = 60       

   
    _NOT_BASE = (5, 5)    
    _NOT_D = 2            
    _NOT_DROW = 0          
    _NOT_DELAY = 2         
    _NOT_STEPS = 60       

    @staticmethod
    def _place(life, offsets, index):
        """Stamp a set of (row, col) offsets as live cells at `index`."""
        for i in range(len (offsets)):
            rr, cc = index[0] + offsets[i][0], index[1] + offsets[i][1]
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
        if bool(region_alive) and int(grid.sum()) == 4:
            return True
        else:
             return False

    def setup_and_gate(self, grid_size=35, input_a_present=False, input_b_present=False):
        
        life = GameOfLife(N=grid_size, finite=True, fastMode=True)
        life._pending_insert = None

        if input_a_present:
            self._place(life, self._SE, self._AND_BASE)

        if input_b_present:
            b_index = (self._AND_BASE[0] + self._AND_DROW, self._AND_BASE[1] + self._AND_D)
            life._pending_insert = (self._AND_DELAY, self._SW, b_index)

        return life

    def setup_not_gate(self, grid_size=35, input_a_present=False):
        
        life = GameOfLife(N=grid_size, finite=True, fastMode=True)
        life._pending_insert = None

        
        self._place(life, self._SE, self._NOT_BASE)

        if input_a_present:
            a_index = (self._NOT_BASE[0] + self._NOT_DROW, self._NOT_BASE[1] + self._NOT_D)
            life._pending_insert = (self._NOT_DELAY, self._SW, a_index)

        return life

    def run_and_gate(self, input_a_present, input_b_present):
        
        life = self.setup_and_gate(
            input_a_present=input_a_present, input_b_present=input_b_present
        )

        for i in range(self._AND_STEPS):
            life.evolve()
            if life._pending_insert and i + 1 == life._pending_insert[0]:
                _, offsets, index = life._pending_insert
                self._place(life, offsets, index)
                life._pending_insert = None

        return self._is_block_at(life.getStates(), self._AND_TARGET)

    def run_not_gate(self, input_a_present):
        
        life = self.setup_not_gate(input_a_present=input_a_present)

        for i in range(self._NOT_STEPS):
            life.evolve()
            if life._pending_insert and i + 1 == life._pending_insert[0]:
                _, offsets, index = life._pending_insert
                self._place(life, offsets, index)
                life._pending_insert = None

        
        if int(life.getStates().sum()) > 0:
            return True
        else:
            return False
