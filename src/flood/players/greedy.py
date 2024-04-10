from flood.board import Board
from flood.players.base import BasePlayer


class GreedyPlayer(BasePlayer):
    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        colors = list(board.get_valid_moves(start_pos, opponent_start_pos))

        best_color = colors[0]
        most_flooded = board.do_move(start_pos, colors[0]).count_flooded_cells(
            start_pos
        )

        for color in colors[1:]:
            flooded = board.do_move(start_pos, color).count_flooded_cells(start_pos)

            if flooded > most_flooded:
                most_flooded = flooded
                best_color = color

        return best_color
