# -*- coding: utf-8 -*-
"""
Visualize a logic-gate simulation with a marker drawn at a fixed grid
position, so you can see where the expected output should appear even
if nothing actually lands there yet.
"""

from pickle import TRUE
import pygame

from logic_gates import GliderLogicGates
from pygame_viewer import grid_to_surface


def run_with_marker(life, target, cell_scale=14, fps=10, max_frames=None,
                     title="Game of Life", marker_color=(255, 0, 0)):
    """Same loop as pygame_viewer.run_pygame_life, plus a marker overlay.

    Args:
        life: a GameOfLife instance (already set up).
        target: (row, col) tuple - the cell to mark, e.g. (15, 12).
        marker_color: RGB color for the marker outline.
    """
    pygame.init()
    cells = life.getStates()
    surface = grid_to_surface(cells, cell_scale=cell_scale)
    screen = pygame.display.set_mode(surface.get_size())
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    tr, tc = target
    # Marker rectangle covers a 2x2 cell area (matches the block size),
    # in screen pixel coordinates. Note: grid_to_surface swaps axes
    # (col -> x, row -> y), so x uses the column and y uses the row.
    marker_rect = pygame.Rect(
        tc * cell_scale, tr * cell_scale,
        2 * cell_scale, 2 * cell_scale,
    )

    finished = False
    frame = 0
    while not finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True

        screen.blit(surface, (0, 0))
        # Draw the marker on top, regardless of what's actually there.
        pygame.draw.rect(screen, marker_color, marker_rect, width=2)
        pygame.display.flip()

        life.evolve()
        cells = life.getStates()
        surface = grid_to_surface(cells, cell_scale=cell_scale)

        frame += 1
        if max_frames is not None and frame >= max_frames:
            finished = True

        clock.tick(fps)

    pygame.quit()


def main():
    gates = GliderLogicGates()

    # Try all four AND-gate input combinations by changing these:
    input_a_present = True
    input_b_present = True

    life = gates.setup_and_gate(
        input_a_present=input_a_present, input_b_present=input_b_present
    )

    # Replay the same delayed-insertion logic run_and_gate() uses, one
    # generation at a time inside the viewer loop below instead of all
    # at once, so you can watch the collision happen.
    pending = life._pending_insert

    class SteppedLife:
        """Thin wrapper so run_with_marker's life.evolve() also applies
        the pending (delayed) glider insertion at the right generation."""
        def __init__(self, life, pending):
            self._life = life
            self._pending = pending
            self._gen = 0

        def __getattr__(self, name):
            return getattr(self._life, name)

        def evolve(self):
            self._life.evolve()
            self._gen += 1
            if self._pending and self._gen == self._pending[0]:
                _, offsets, index = self._pending
                gates._place(self._life, offsets, index)
                self._pending = None

    wrapped = SteppedLife(life, pending)

    run_with_marker(
        wrapped,
        target=gates._AND_TARGET,   # (15, 12)
        cell_scale=14,
        fps=1,
        max_frames=gates._AND_STEPS+100,
        title=f"AND gate  A={int(input_a_present)} B={int(input_b_present)}",
    )


if __name__ == "__main__":
    main()
