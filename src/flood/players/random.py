from flood.board import Board
from flood.players.base import BasePlayer
import random


class RandomPlayer(BasePlayer):
    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        # Find any move that isn't played just before.
        colors = board.get_remaining_colors()
        current_color = board.get_color(*start_pos)
        colors = colors - {current_color}

        # Pick random color.
        return random.choice(list(colors))
