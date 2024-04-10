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
        colors = board.get_valid_moves(start_pos, opponent_start_pos)
        return random.choice(list(colors))
