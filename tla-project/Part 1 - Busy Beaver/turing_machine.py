
import logging
from itertools import islice
from tabnanny import check

class TuringMachine:

    def __init__(self, transitions, start_state='q0', accept_state='qa', reject_state='qr', blank_symbol=''):
        self.transitions = transitions
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.blank_symbol = blank_symbol

    def run(self, input_):
        
        if input_ :
            tape = list (input_)
        else:
            tape = [self.blank_symbol]
        if not tape:
            tape = [self.blank_symbol]
            
        pos = 0
        state = self.start_state

        while True:
            if pos < 0:
                tape.insert(0, self.blank_symbol)
                pos = 0
            elif pos >= len(tape):
                tape.append(self.blank_symbol)


            left_hand_side = []
            right_hand_side =[]
            for i in range(len(tape)):
                if i<pos:
                    left_hand_side.append(tape[i])
                elif i==pos:
                    current_symbol = tape[pos]
                else:
                    right_hand_side.append(tape[i])

            config = {
                'state': state,
                'left_hand_side': left_hand_side,
                'symbol': current_symbol,
                'right_hand_side': right_hand_side
            }

            if state == self.accept_state:
                yield ('Accept', config)
                break

            if state == self.reject_state:
                yield ('Reject', config)
                break
            
            check = (state, current_symbol)
            if check not in self.transitions:
                yield ('Reject', config)
                break

            yield (None, config)

            new_state, write_symbol, direction = self.transitions[check]
            
            tape[pos] = write_symbol
            state = new_state

            if direction == 'L':
                pos -= 1
            elif direction == 'R':
                pos += 1
            elif direction == 'S':
                pos = pos
            else:
                raise ValueError(f"Invalid direction: {direction}")

    def accepts(self, input_, step_limit=100):
        gen = self.run(input_)
        steps = 0
        for action, _ in gen:
            if action == 'Accept':
                return True
            if action == 'Reject':
                return False
            steps += 1
            if steps >= step_limit:
                return None
        return False

    def rejects(self, input_, **kwargs):
        res = self.accepts(input_, **kwargs)
        if res is None: return None
        return not res

    def debug(self, input_, step_limit=100, colored=False):
        gen = self.run(input_)
        for i, (action, config) in enumerate(gen):
            if i >= step_limit:
                print("step limit reached")
                break
            
            left =""
            right=""
            for i in range (len(config["left_hand_side"])):
                left += config["left_hand_side"][i]
            for i in range (len(config["right_hand_side"])):
                right += config["right_hand_side"][i]
            sym = config["symbol"]
            output = f" {left}[{sym}]{right}"
            if action:
                output += f" -> {action}"
            print(output)

new1 = TuringMachine(transitions = {
        ('q0', '#'): ('End', '#', 'R'),
        ('End', ''): ('qa', '', 'R'),

        ('q0', '0'): ('FindDelimiter0', 'X', 'R'),
        ('FindDelimiter0', '#'): ('Check0', '#', 'R'),
        ('Check0', '0'): ('FindLeftmost', 'X', 'L'),

        ('q0', '1'): ('FindDelimiter1', 'X', 'R'),
        ('FindDelimiter1', '#'): ('Check1', '#', 'R'),
        ('Check1', '1'): ('FindLeftmost', 'X', 'L'),

        ('FindLeftmost', '0'): ('FindLeftmost', '0', 'L'),
        ('FindLeftmost', '1'): ('FindLeftmost', '1', 'L'),
        ('FindLeftmost', 'X'): ('FindLeftmost', 'X', 'L'),
        ('FindLeftmost', '#'): ('FindLeftmost', '#', 'L'),
        ('FindLeftmost', ''): ('FindNext', '', 'R'),

        ('FindNext', 'X'): ('FindNext', 'X', 'R'),
        ('FindNext', '0'): ('FindDelimiter0', 'X', 'R'),
        ('FindNext', '1'): ('FindDelimiter1', 'X', 'R'),
        ('FindNext', '#'): ('End', '#', 'R'),

        ('FindDelimiter0', '0'): ('FindDelimiter0', '0', 'R'),
        ('FindDelimiter0', '1'): ('FindDelimiter0', '1', 'R'),
        ('FindDelimiter1', '0'): ('FindDelimiter1', '0', 'R'),
        ('FindDelimiter1', '1'): ('FindDelimiter1', '1', 'R'),

        ('Check0', 'X'): ('Check0', 'X', 'R'),
        ('Check1', 'X'): ('Check1', 'X', 'R'),

        ('End', 'X'): ('End', 'X', 'R')
})

new1.accepts("11#XXXX1")
