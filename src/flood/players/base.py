from typing import Optional

from flood.board import Board


class BasePlayer:
    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: Optional[tuple[int, int]],
        timeout: Optional[float] = None,
    ) -> int:
        """
        Compute the next move.

        Args:
            board (Board): The position to do a move on.
            start_pos (tuple[int, int]): The starting position of the player, typically
                located at the top-left corner of the board, provided in (x, y) tuple format.
            opponent_start_pos (Optional[tuple[int, int]]): The starting position of the
                opponent, if present, in the same (x, y) tuple format. If there is no
                opponent, this parameter should be set to None.
            timeout (Optional[float], optional): The time limit, in seconds, within which
                the function must return a move. If not specified, the function may take
                an arbitrary amount of time. Defaults to None.

        Returns:
            int: The color chosen for the next move. This integer represents the color
                that the player intends to flood the board with in order to win the game.
        """
        raise NotImplementedError
