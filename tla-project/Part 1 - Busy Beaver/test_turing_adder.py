# -*- coding: utf-8 -*-
from turing_machine import TuringMachine

transitions = {
    # Phase 1: Look for the separator '0'
    ('q0', '1'): ('q0', '1', 'R'),
    ('q0', '0'): ('find_end', '1', 'R'),  # Replace 0 with 1
    
    # Phase 2: Go to the end of the combined string
    ('find_end', '1'): ('find_end', '1', 'R'),
    ('find_end', ''): ('remove_extra', '', 'L'),
    
    # Phase 3: Remove the last 1 to correct the count (n+m)
    ('remove_extra', '1'): ('qa', '', 'R'),
}

if __name__ == "__main__":
    machine = TuringMachine(transitions, blank_symbol='')
    input_str = "110111" # 2 + 3
    print(f"Running Addition on {input_str}...")
    machine.debug(input_str)

if __name__ == "__main__":
    print_states(transitions)
    machine = TuringMachine(transitions)

    def run(input_):
        w = input_
        print("Input:",w)
        print("Accepted" if machine.accepts(w) else "Rejected")
        machine.debug(w)
        print()

    # SHOULD ACCEPT
    run("110111")
    # outputs 11111

    # SHOULD ACCEPT
    run("11101111")
    #     # outputs 1111111
    run("0111")
    # outputs 111