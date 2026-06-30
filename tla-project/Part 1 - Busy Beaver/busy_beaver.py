# -*- coding: utf-8 -*-
from turing_machine import TuringMachine

# BB(2) Champion: 6 steps, 4 ones
bb2_trans = {
    ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('b', '1', 'L'),
    ('b', '0'): ('a', '1', 'L'), ('b', '1'): ('h', '1', 'R'),
}

# BB(3) Champion: 21 steps, 5 ones
bb3_trans = {
    ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('h', '1', 'L'),
    ('b', '0'): ('c', '0', 'R'), ('b', '1'): ('b', '1', 'R'),
    ('c', '0'): ('c', '1', 'L'), ('c', '1'): ('a', '1', 'L'),
}

# BB(4) Champion: 107 steps, 13 ones
bb4_trans = {
    ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('b', '1', 'L'),
    ('b', '0'): ('a', '1', 'L'), ('b', '1'): ('c', '0', 'L'),
    ('c', '0'): ('h', '1', 'R'), ('c', '1'): ('d', '1', 'L'),
    ('d', '0'): ('d', '1', 'R'), ('d', '1'): ('a', '0', 'R'),
}

# BB(5) High Performer: 47,176,870 steps, 4098 ones
bb5_trans = {
    ('a', '0'): ('b', '1', 'R'), ('a', '1'): ('c', '1', 'L'),
    ('b', '0'): ('c', '1', 'R'), ('b', '1'): ('b', '1', 'R'),
    ('c', '0'): ('d', '1', 'R'), ('c', '1'): ('e', '0', 'L'),
    ('d', '0'): ('a', '1', 'L'), ('d', '1'): ('d', '1', 'L'),
    ('e', '0'): ('h', '1', 'R'), ('e', '1'): ('a', '0', 'L'),
}

bbeaver2 = TuringMachine(bb2_trans, start_state='a', accept_state='h', blank_symbol='0')
bbeaver3 = TuringMachine(bb3_trans, start_state='a', accept_state='h', blank_symbol='0')
bbeaver4 = TuringMachine(bb4_trans, start_state='a', accept_state='h', blank_symbol='0')
bbeaver5 = TuringMachine(bb5_trans, start_state='a', accept_state='h', blank_symbol='0')