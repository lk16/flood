from copy import copy
import datetime
from flood.board import Board
from flood.players.graph.graph import Graph


class SolutionFound(Exception):
    def __init__(self, moves: list[int]) -> None:
        self.moves = moves


class GraphSinglePlayerSolver:
    def __init__(self, graph: Graph, start_node_id: int) -> None:
        self.graph = graph
        self.start_node_id = start_node_id
        self.max_moves = 0

        # to observe search speed
        self.solve_start = datetime.datetime.now()
        self.attempts = 0

    def _get_newly_flooded(self, flooded: set[int], move: int) -> set[int]:
        newly_flooded: set[int] = set()

        for flooded_node in flooded:
            for neighbour_node in self.graph.neighbours[flooded_node]:
                if (
                    neighbour_node not in flooded
                    and self.graph.colors[neighbour_node] == move
                ):
                    newly_flooded.add(neighbour_node)

        return newly_flooded

    def _count_unflooded_colors(self, flooded: set[int]) -> int:
        unflooded_nodes = set(range(self.graph.node_count())) - flooded
        unflooded_colors = {self.graph.colors[node] for node in unflooded_nodes}
        return len(unflooded_colors)

    def _print_speed(self) -> None:
        seconds = (datetime.datetime.now() - self.solve_start).total_seconds()
        speed = self.attempts / seconds
        print(
            f"{self.attempts:>10} attempts / {seconds:7.2f} sec = {speed:6.0f} attempts / sec"
        )

    def _solve(self, flooded: set[int], moves: list[int]) -> None:
        if len(moves) > self.max_moves:
            return

        if self._count_unflooded_colors(flooded) + len(moves) > self.max_moves:
            return

        if len(flooded) == self.graph.node_count():
            raise SolutionFound(moves)

        self.attempts += 1
        if self.attempts % 10000 == 0:
            self._print_speed()

        valid_moves = set(self.graph.colors)
        if moves:
            valid_moves -= {moves[-1]}

        move_tuples: list[tuple[int, int, set[int]]] = []

        for move in valid_moves:
            newly_flooded = self._get_newly_flooded(flooded, move)
            heuristic = len(newly_flooded)
            move_tuple = (move, heuristic, newly_flooded)

            if newly_flooded:
                move_tuples.append(move_tuple)

        move_tuples = sorted(move_tuples, key=lambda t: -t[1])

        for move, _, newly_flooded in move_tuples:
            self._solve(flooded | newly_flooded, copy(moves) + [move])

    def solve(self) -> int:
        self.solve_start = datetime.datetime.now()
        self.attempts = 0

        # TODO Don't hardcode
        self.max_moves = 80

        best_move = -1

        while True:
            try:
                self._solve({self.start_node_id}, [])
            except SolutionFound as solution:
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

        self._print_speed()

        assert best_move != -1
        return best_move
