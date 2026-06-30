# -*- coding: utf-8 -*-
from turing_machine import TuringMachine

transitions = {
    # Start: Mark a '1' in group 1 with 'X'
    ('q0', '1'): ('find_group2', 'X', 'R'),
    ('q0', '0'): ('cleanup', '', 'R'), # Done marking group 1

    # Find the start of group 2
    ('find_group2', '1'): ('find_group2', '1', 'R'),
    ('find_group2', '0'): ('copy_loop', '0', 'R'),

    # Inside group 2: Mark a '1' with 'Y', then go to far end to add a '1'
    ('copy_loop', '1'): ('to_far_end', 'Y', 'R'),
    ('copy_loop', '0'): ('reset_group2', '0', 'L'), # Group 2 fully copied for this X
    ('copy_loop', ''): ('reset_group2', '', 'L'), 

    # Move to the very end of the tape to write the result '1'
    ('to_far_end', '1'): ('to_far_end', '1', 'R'),
    ('to_far_end', '0'): ('to_far_end', '0', 'R'),
    ('to_far_end', ''): ('back_to_group2', '1', 'L'), # Write '1' at end

    # Move back to find the next 'Y' in group 2
    ('back_to_group2', '1'): ('back_to_group2', '1', 'L'),
    ('back_to_group2', '0'): ('back_to_group2', '0', 'L'),
    ('back_to_group2', 'Y'): ('copy_loop', 'Y', 'R'), # Resume copying

    # Reset Y markers to 1 and return to find next '1' in group 1
    ('reset_group2', 'Y'): ('reset_group2', '1', 'L'),
    ('reset_group2', '1'): ('reset_group2', '1', 'L'),
    ('reset_group2', '0'): ('reset_group2', '0', 'L'),
    ('reset_group2', 'X'): ('q0', 'X', 'R'), # Look for next '1'

    # Cleanup: Erase everything before the result string
    ('cleanup', '1'): ('cleanup', '', 'R'),
    ('cleanup', '0'): ('cleanup', '', 'R'),
    ('cleanup', ''): ('qa', '', 'R'),
}

if __name__ == "__main__":
    machine = TuringMachine(transitions, blank_symbol='')
    input_str = "110111" # 2 * 3
    print(f"Running Multiplication on {input_str}...")
    machine.debug(input_str, step_limit=500)