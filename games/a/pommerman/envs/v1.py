from . import utility
from . import v0


class Pomme(v0.Pomme):
    """This environment is the same as v0.Pomme, except it collapses the board at certain intervals."""
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : utility.RENDER_FPS
    }

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        first_collapse = kwargs.get('first_collapse')
        self.collapses = list(range(
            first_collapse, self._max_steps, int((self._max_steps - first_collapse)/self._board_size)
        ))

    def _collapse_board(self, ring):
        """Collapses the board at a certain ring radius.

        For example, if the board is 13x13 and ring is 0, then the the ring of the first row, last row,
        first column, and last column is all going to be turned into rigid walls. All agents in that ring
        die and all bombs are removed without detonating.

        For further rings, the values get closer to the center.

        Args:
          ring: Integer value of which cells to collapse.
        """
        board = self._board.copy()

        def collapse(r, c):
            if utility.position_is_agent(board, (r, c)):
                # Agent. Kill it.
                num_agent = board[r][c] - utility.Item.Agent1.value
                agent = self._agents[num_agent]
                agent.die()
            elif utility.position_is_bomb(board, (r, c)):
                # Bomb. Remove the bomb.
                self._bombs = [b for b in self._bombs if b.position != (r, c)]
            elif (r, c) in self._items:
                # Item. Remove the item.
                del self._items[(r, c)]
            board[r][c] = utility.Item.Rigid.value

        for cell in range(ring, self._board_size - ring):
            collapse(ring, cell)
            if ring != cell:
                collapse(cell, ring)

            end = self._board_size - ring - 1
            collapse(end, cell)
            if end != cell:
                collapse(cell, end)

        return board
