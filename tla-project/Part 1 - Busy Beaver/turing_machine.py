# -*- coding: utf-8 -*-
import logging

class TuringMachine:
    """
    A robust Turing Machine simulator with a bidirectional infinite tape.
    """

    def __init__(self, transitions, start_state='q0', accept_state='qa', reject_state='qr', blank_symbol=''):
        self.transitions = transitions
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.blank_symbol = blank_symbol

    def run(self, input_):
        """
        Executes the Turing machine as a Python Generator.
        Yields (action, configuration) at each step.
        """
        # Initialize tape as a list.
        tape = list(input_) if input_ else [self.blank_symbol]
        if not tape:
            tape = [self.blank_symbol]
            
        pos = 0
        state = self.start_state

        while True:
            # 1. Handle Infinite Tape (Dynamic Expansion)
            if pos < 0:
                tape.insert(0, self.blank_symbol)
                pos = 0
            elif pos >= len(tape):
                tape.append(self.blank_symbol)

            # 2. Prepare Configuration
            # LHS: symbols on left in REVERSE order (closest to head is last)
            left_hand_side = tape[:pos][::-1] 
            current_symbol = tape[pos]
            right_hand_side = tape[pos + 1:]

            config = {
                'state': state,
                'left_hand_side': left_hand_side,
                'symbol': current_symbol,
                'right_hand_side': right_hand_side
            }

            # 3. Check Halt Conditions
            if state == self.accept_state:
                yield ('Accept', config)
                break
            if state == self.reject_state:
                yield ('Reject', config)
                break

            # 4. Fetch Transition
            lookup = (state, current_symbol)
            if lookup not in self.transitions:
                yield ('Reject', config)
                break

            # Yield current state before executing the transition
            yield (None, config)

            # 5. Execute Transition
            new_state, write_symbol, direction = self.transitions[lookup]
            
            tape[pos] = write_symbol
            state = new_state

            # 6. Move Head
            if direction.upper() == 'L':
                pos -= 1
            elif direction.upper() == 'R':
                pos += 1
            else:
                raise ValueError(f"Invalid direction: {direction}")

    def accepts(self, input_, step_limit=10000):
        """Returns True if accepted, False if rejected, None if limit reached."""
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
        """Exact opposite of accepts."""
        res = self.accepts(input_, **kwargs)
        if res is None: return None
        return not res

    def debug(self, input_, step_limit=100, colored=False):
        """Prints state_name left[symbol]right."""
        gen = self.run(input_)
        for i, (action, config) in enumerate(gen):
            if i >= step_limit:
                print("... step limit reached ...")
                break
            
            # For display purposes in debug, we show the tape in natural order
            # but the logic uses reversed LHS as per spec.
            lhs = "".join(config['left_hand_side'][::-1])
            sym = config['symbol']
            rhs = "".join(config['right_hand_side'])
            state = config['state']
            
            output = f"{state:10} {lhs}[{sym}]{rhs}"
            if action:
                output += f" -> {action}"
            print(output)