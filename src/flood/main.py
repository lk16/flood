from time import sleep
import random
from typing import Optional, Type
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
    def command(
        player_name: str,
        width: int = typer.Option(10, "-w", "--width"),
        height: int = typer.Option(10, "-h", "--height"),
        colors: int = typer.Option(5, "-c", "--colors"),
        seed: Optional[int] = typer.Option(None, "-s", "--seed"),
        delay: Optional[float] = typer.Option(None, "-d", "--delay"),
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
        start_pos = (0, 0)

        while not board.is_solved():
            board.print()
            move = player.get_best_move(board, start_pos, None, None)
            board = board.do_move(start_pos, move)
            print()

            if delay is not None:
                sleep(delay)

        board.print()

    typer.run(command)
