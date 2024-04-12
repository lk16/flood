from time import sleep
import random
from typing import Optional, Type
from flood.board import Board
import typer

from flood.players.base import BasePlayer
from flood.players.greedy import GreedyPlayer
from flood.players.kurt import KurtPlayer
from flood.players.random import RandomPlayer

PLAYER_TYPES: dict[str, Type[BasePlayer]] = {
    # Please keep this sorted alphabetically
    "greedy": GreedyPlayer,
    "kurt": KurtPlayer,
    "random": RandomPlayer,
}


def solve() -> None:
    def command(
        player_name: str,
        width: int = typer.Option(10, "-w", "--width"),
        height: int = typer.Option(10, "-h", "--height"),
        colors: int = typer.Option(5, "-c", "--colors"),
        seed: Optional[int] = typer.Option(None, "-s", "--seed"),
        print_delay: Optional[float] = typer.Option(None, "-d", "--delay"),
    ) -> None:
        try:
            player_type = PLAYER_TYPES[player_name]
        except KeyError:
            print(f'No player named "{player_name}"')
            raise SystemExit(1)

        player = player_type()

        if seed is not None:
            random.seed(seed)

        board = Board.random(height, width, colors)
        board.print()
        print()

        moves: list[int] = []
        start_pos = (0, 0)

        while not board.is_solved():
            move = player.get_best_move(board, start_pos, None, None)
            moves.append(move)
            board = board.do_move(start_pos, move)
            board.print()
            print()
            print(f"Moves ({len(moves)}): ", end="")
            print(" ".join(board.get_printed_string_for_color(move) for move in moves))
            print()
            print()

            if print_delay is not None:
                sleep(print_delay)

    typer.run(command)
