from copy import copy
import datetime
import json
import os

from pathlib import Path
import subprocess
from flood.board import Board
from flood.players.graph.graph import Graph
from flood.players.graph.types import BitSet, SolutionFound


class GraphSinglePlayerSolver:
    def __init__(self, graph: Graph, start_node_id: int) -> None:
        self.graph = graph
        self.start_node_id = start_node_id
        self.max_moves = 0

        # to observe search speed
        self.solve_start = datetime.datetime.now()
        self.attempts = 0

    def _get_newly_flooded(self, flooded: BitSet, move: int) -> BitSet:
        unflooded_color_set = BitSet(self.graph.colors[move] & ~flooded)
        after = BitSet(0)
        for node in unflooded_color_set:
            neighbours = self.graph.neighbours[node]
            if neighbours & flooded:
                after = BitSet(after | (1 << node))

        return after

    def _count_unflooded_colors(self, flooded_bitset: BitSet) -> int:
        unflooded_colors = 0
        for color_set in self.graph.colors:
            if color_set & ~flooded_bitset:
                unflooded_colors += 1

        return unflooded_colors

    def _print_speed(self) -> None:
        seconds = (datetime.datetime.now() - self.solve_start).total_seconds()
        speed = self.attempts / seconds
        print(
            f"{self.attempts:>10} attempts / {seconds:7.2f} sec = {speed:6.0f} attempts / sec"
        )

    def _solve(self, flooded: BitSet, moves: list[int]) -> None:
        if len(moves) > self.max_moves:
            return

        if self._count_unflooded_colors(flooded) + len(moves) > self.max_moves:
            return

        if flooded.count() == self.graph.node_count():
            raise SolutionFound(moves)

        self.attempts += 1
        if self.attempts % 10000 == 0:
            self._print_speed()

        valid_moves = set(range(self.graph.color_count()))
        if moves:
            valid_moves -= {moves[-1]}

        move_tuples: list[tuple[int, int, BitSet]] = []

        for move in valid_moves:
            newly_flooded = self._get_newly_flooded(flooded, move)
            heuristic = newly_flooded.count()
            move_tuple = (move, heuristic, newly_flooded)

            if newly_flooded:
                move_tuples.append(move_tuple)

        move_tuples = sorted(move_tuples, key=lambda t: -t[1])

        for move, _, newly_flooded in move_tuples:
            child_flooded = BitSet(flooded | newly_flooded)
            self._solve(child_flooded, copy(moves) + [move])

    def solve(self) -> int:
        if "FLOOD_GRAPH_PLAYER_USE_RUST" in os.environ:
            return self._solve_with_rust()

        self.solve_start = datetime.datetime.now()
        self.attempts = 0

        best_move = -1
        self.max_moves = self.graph.node_count()

        while True:
            initial_flooded = BitSet(1 << self.start_node_id)

            try:
                self._solve(initial_flooded, [])
            except SolutionFound as solution:
                self._print_speed()
                print(f"Found solution ({len(solution.moves)}): ", end="")
                print(
                    " ".join(
                        Board.get_printed_string_for_color(move)
                        for move in solution.moves
                    )
                )
                print()

                self.max_moves = len(solution.moves) - 1
                best_move = solution.moves[0]
            else:
                break

        assert best_move != -1
        return best_move

    def _solve_with_rust(self) -> int:
        executable = Path(__file__).parent / "target/release/graph"

        if not executable.exists():
            raise Exception(f"Rust executable was not found at {executable}")
        node_ids = list(range(self.graph.node_count()))

        arguments = {
            "start": self.start_node_id,
            "colors": [self.graph.get_color(node) for node in node_ids],
            "neighbours": [self.graph.get_neighbour_list(node) for node in node_ids],
        }

        process = subprocess.Popen(
            [executable, json.dumps(arguments)],
            stdout=subprocess.PIPE,
        )

        assert process.stdout

        while True:
            raw_line = process.stdout.readline()
            if raw_line == b"":
                break

            line = raw_line.decode()
            print(line, end="")

            if line.startswith("Solution:"):
                return int(line.split(" ")[1])

        # Unreachable
        raise NotImplementedError
