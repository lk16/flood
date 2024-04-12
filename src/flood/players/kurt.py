from collections import Counter

from flood.board import Board
from flood.players.base import BasePlayer


class KurtPlayer(BasePlayer):
    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        colors = list(board.get_valid_moves(start_pos, opponent_start_pos))

        current_flooded = board.count_flooded_cells(start_pos)
        adjacent_colors = []
        for color in colors:
            possible_flooded = board.do_move(start_pos, color).count_flooded_cells(
                start_pos
            )
            if possible_flooded > current_flooded:
                adjacent_colors.append(color)

        most_flooded_percentage = 0.0

        for color in adjacent_colors:
            future_board = board.do_move(start_pos, color)
            flooded = future_board.count_flooded_cells(start_pos)
            flooded_percentage = flooded / Counter(future_board.get_fields())[color]

            if flooded_percentage > most_flooded_percentage:
                most_flooded_percentage = flooded_percentage
                best_color = color

        return best_color
