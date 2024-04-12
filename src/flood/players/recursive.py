from flood.board import Board
from flood.players.base import BasePlayer


class RecursivePlayer(BasePlayer):
    def evaluate_board(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        layers: int,
        next_best_color: int | None,
    ) -> tuple[int | None, int, int | None]:
        colors = list(board.get_valid_moves(start_pos, opponent_start_pos))

        field_count = len(board.get_fields())

        if next_best_color:
            adjacent_colors = [next_best_color]
        else:
            current_flooded = board.count_flooded_cells(start_pos)
            adjacent_colors = []
            for color in colors:
                possible_flooded = board.do_move(start_pos, color).count_flooded_cells(
                    start_pos
                )
                if possible_flooded > current_flooded:
                    adjacent_colors.append(color)

        if not adjacent_colors:
            return None, field_count, None

        if len(adjacent_colors) == 1:
            return adjacent_colors[0], field_count, None

        most_flooded = 0
        best_color = None
        next_best_color = None

        for color in adjacent_colors:
            future_board = board.do_move(start_pos, color)

            if layers == 1:
                flooded = future_board.count_flooded_cells(start_pos)

                if flooded > most_flooded:
                    most_flooded = flooded
                    best_color = color
            else:
                (
                    future_best_color,
                    flooded,
                    future_next_best_color,
                ) = self.evaluate_board(
                    future_board, start_pos, opponent_start_pos, layers - 1, None
                )
                next_best_color = future_next_best_color

                if flooded > most_flooded:
                    most_flooded = flooded
                    best_color = color

        return best_color, most_flooded, next_best_color

    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        best_color, _, _ = self.evaluate_board(
            board, start_pos, opponent_start_pos, 7, None
        )

        assert best_color is not None
        return best_color
