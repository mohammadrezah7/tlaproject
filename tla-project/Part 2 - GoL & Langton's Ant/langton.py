
import numpy as np


class LangtonsAnt:
    

    
    _DIRECTIONS = ('U', 'R', 'D', 'L')
    
    _DIRECTION_DELTAS = {
        'U': (-1, 0),
        'R': (0, 1),
        'D': (1, 0),
        'L': (0, -1),
    }

    def __init__(self, N, ant_position, rules):
        
        self.N = N
        self.grid = np.zeros((N, N), dtype=int)
        self.position = [ant_position[0] % N, ant_position[1] % N]
        self.rules = rules
        
        self.direction_index = 0

    def get_states(self):
        
        return self.grid

    def get_current_position(self):
        
        return tuple(self.position)

    def step(self):
        
        r, c = self.position
        current_color = int(self.grid[r, c])

        next_color, turn_direction = self.rules[current_color]

      
        self.grid[r, c] = next_color

        
        if turn_direction == 'R':
            self.direction_index = (self.direction_index + 1) % 4
        elif turn_direction == 'L':
            self.direction_index = (self.direction_index - 1) % 4
        

        
        heading = self._DIRECTIONS[self.direction_index]
        dr, dc = self._DIRECTION_DELTAS[heading]
        self.position = [(r + dr) % self.N, (c + dc) % self.N]

    def update(self):
      
        self.step()
