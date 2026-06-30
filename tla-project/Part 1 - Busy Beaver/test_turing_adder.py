
from turing_machine import TuringMachine
from test_turing_machine_example1 import print_states

transitions = {
        ('q0', '1'): ('q0', '1', 'R'),
        ('q0', '0'): ('find_end', '1', 'R'),
    
        ('find_end', '1'): ('find_end', '1', 'R'),
        ('find_end', ''): ('remove_extra', '', 'L'),
    
        ('remove_extra', '1'): ('qa', '', 'R'),
}

if __name__ == "__main__":
    print_states(transitions)
    machine = TuringMachine(transitions)

    def run(input_):
        w = input_
        print("Input:",w)
        print("Accepted" if machine.accepts(w) else "Rejected")
        machine.debug(w)
        print()

    
    run("110111")
    
    run("11101111")

    run("0111")
