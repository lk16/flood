from typing import Type
from flood.board import Board
import typer

from flood.players.base import BasePlayer
from flood.players.greedy import GreedyPlayer
from flood.players.random import RandomPlayer

PLAYER_TYPES: dict[str, Type[BasePlayer]] = {
    # Please keep this sorted alphabetically
    "greedy": GreedyPlayer,
    "random": RandomPlayer,
}


def solve() -> None:
    def command(player_name: str) -> None:
        try:
            player_type = PLAYER_TYPES[player_name]
        except KeyError:
            print(f'No player named "{player_name}"')
            raise SystemExit(1)

        player = player_type()

        board = Board.random(8, 8, 4)  # TODO make these flags
        start_pos = (0, 0)

        while not board.is_solved():
            board.print()
            move = player.get_best_move(board, start_pos, None, None)
            board = board.do_move(start_pos, move)
            print()

        board.print()

    typer.run(command)
