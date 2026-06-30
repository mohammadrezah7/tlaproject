
from turing_machine import TuringMachine
from test_turing_machine_example1 import print_states

transitions = {
    
    ('q0', '1'): ('q1', 'X', 'R'),
    ('q0', '0'): ('q7', '0', 'L'),
       
    ('q1', '1'): ('q1', '1', 'R'),
    ('q1', '0'): ('q2', '0', 'R'),
    
    ('q2', '1'): ('q2', 'Y', 'R'),
    ('q2', ''): ('q3', '', 'L'),
    ('q2','Z'): ('q3', 'Z','L'),
       
    ('q3', 'Y'): ('q4', '1', 'R'),

    ('q4', 'Z'): ('q4', 'Z', 'R'),
    ('q4', '1'): ('q4', '1', 'R'),
    ('q4', ''): ('q5', 'Z', 'L'),

    ('q5', 'Y'): ('q4', '1', 'R'),
    ('q5', 'Z'): ('q5', 'Z', 'L'),
    ('q5', '1'): ('q5', '1', 'L'),
    ('q5', '0'):  ('q6', '0', 'L'),

    ('q6', '1'): ('q6', '1', 'L'),
    ('q6', 'X'): ('q0', 'X', 'R'),

    ('q7', 'X'): ('q7', 'X', 'L'),
    ('q7', ''): ('q8', '', 'R'),

    ('q8', '1'): ('q8', '', 'R'),   
    ('q8', 'Z'): ('q8', '1', 'R'),   
    ('q8', 'X'): ('q8', '', 'R'),   
    ('q8', 'Y'): ('q8', '', 'R'),   
    ('q8', '0'): ('q8', '', 'R'),   
    ('q8',''): ('qa','','S')

}

if __name__ == "__main__":
    print_states(transitions)
    machine = TuringMachine(transitions)

    def run(input_):
        w = input_
        print("Input:",w)
        print("Accepted" if machine.accepts(w) else "Rejected")
        machine.debug(w, step_limit=1000)

        print()

    
    run("1110111")
    
    run("11101111")

    run("01111")
