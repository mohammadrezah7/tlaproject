# -*- coding: utf-8 -*-
import sys

class Error(Exception):
    pass

class TuringMachine1(object):
    def __init__(self, program, start, halt, init):
        self.program = program
        self.start = start
        self.halt = halt
        self.init = init
        self.tape = [self.init]
        self.pos = 0
        self.state = self.start
        self.set_tape_callback(None)
        self.tape_changed = 1
        self.movez = 0

    def run(self):
        tape_callback = self.get_tape_callback()
        while self.state != self.halt:
            if tape_callback:
                tape_callback(self.tape, self.tape_changed)

            lhs = self.get_lhs()
            rhs = self.get_rhs(lhs)

            new_state, new_symbol, move = rhs

            old_symbol = lhs[1]
            self.update_tape(old_symbol, new_symbol)
            self.update_state(new_state)
            self.move_head(move)

        if tape_callback:
            tape_callback(self.tape, self.tape_changed)

    def set_tape_callback(self, fn):
        self.tape_callback = fn

    def get_tape_callback(self):
        return self.tape_callback

    property(get_tape_callback, set_tape_callback)

    @property
    def moves(self):
        return self.movez

    def update_tape(self, old_symbol, new_symbol):
        if old_symbol != new_symbol:
            self.tape[self.pos] = new_symbol
            self.tape_changed += 1
        else:
            self.tape_changed = 0

    def update_state(self, state):
        self.state = state

    def get_lhs(self):
        under_cursor = self.tape[self.pos]
        return (self.state, under_cursor)

    def get_rhs(self, lhs):
        if lhs not in self.program:
            raise Error('Could not find transition for state "%s".' % lhs)
        return self.program[lhs]

    def move_head(self, move):
        if move == 'L':
            self.pos -= 1
        elif move == 'R':
            self.pos += 1
        elif move == 'S':
            self.pos += 0
        else:
            raise Error('Unknown move "%s". It can only be left or right.' % move)

        if self.pos < 0:
            self.tape.insert(0, self.init)
            self.pos = 0
        if self.pos >= len(self.tape):
            self.tape.append(self.init)

        self.movez += 1

beaver_programs = [
    { },
    {
       
    },
    {
        
    },
    {
        ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('b', '1', 'L'),
        ('b', '0'): ('a', '1', 'L'), ('b', '1'): ('h', '1', 'R'),
    },
    {
        ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('h', '1', 'L'),
        ('b', '0'): ('c', '0', 'R'), ('b', '1'): ('b', '1', 'R'),
        ('c', '0'): ('c', '1', 'L'), ('c', '1'): ('a', '1', 'L'),
    },
    {
        ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('b', '1', 'L'),
        ('b', '0'): ('a', '1', 'L'), ('b', '1'): ('c', '0', 'L'),
        ('c', '0'): ('h', '1', 'R'), ('c', '1'): ('d', '1', 'L'),
        ('d', '0'): ('d', '1', 'R'), ('d', '1'): ('a', '0', 'R'),
    },
    {
        ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('c', '1', 'L'),
        ('b', '0'): ('c', '1', 'R'), ('b', '1'): ('b', '1', 'R'),
        ('c', '0'): ('d', '1', 'R'), ('c', '1'): ('e', '0', 'L'),
        ('d', '0'): ('a', '1', 'L'), ('d', '1'): ('d', '1', 'L'),
        ('e', '0'): ('h', '1', 'R'), ('e', '1'): ('a', '0', 'L'),
    }
]

def busy_beaver(n):
    def tape_callback(tape, tape_changed):
        if tape_changed:
            print(''.join(tape))

    program = beaver_programs[n]

    print("Running Busy Beaver with %d states." % n)
    tm = TuringMachine1(program, 'a', 'h', '0')
    tm.set_tape_callback(tape_callback)
    tm.run()
    print("Busy beaver finished in %d steps." % tm.moves)

def usage():
    print("Usage: %s [1|2|3|4|5|6]" % sys.argv[0])
    print("Runs Busy Beaver problem for 1 or 2 or 3 or 4 or 5 or 6 states.")
    sys.exit(1)

if __name__ == "__main__":
    # if len(sys.argv[1:]) < 1:
    #     usage()
    #
    # n = int(sys.argv[1])
    #
    # if n < 1 or n > 6:
    #     print("n must be between 1 and 6 inclusive")
    #     print()
    #     usage()
    #
    # busy_beaver(n)
    busy_beaver(3)