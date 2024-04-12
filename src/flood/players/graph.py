from copy import copy
import datetime
from flood.board import Board
from flood.players.base import BasePlayer


def get_node_ids(board: Board) -> list[int]:
    cell_count = board.get_column_count() * board.get_row_count()
    node_ids = [-1] * cell_count
    next_node_id = 0

    for cell_id in range(cell_count):
        if node_ids[cell_id] != -1:
            # cell already has region_id
            continue

        cell_coords = board.get_coordinates(cell_id)
        flooded_cell_ids = board.get_flooded_cells(cell_coords)

        for flooded_cell_id in flooded_cell_ids:
            assert node_ids[flooded_cell_id] == -1
            node_ids[flooded_cell_id] = next_node_id

        next_node_id += 1

    assert all(node_id != -1 for node_id in node_ids)
    return node_ids


def print_node_ids(board: Board, node_ids: list[int]) -> None:
    for y in range(board.get_row_count()):
        for x in range(board.get_column_count()):
            index = board.get_index(x, y)
            assert node_ids[index] is not None
            print(f"{node_ids[index]:>2}", end="")
        print()


def get_node_colors(board: Board, node_ids: list[int]) -> list[int]:
    cell_count = board.get_column_count() * board.get_row_count()

    node_count = max(node_ids) + 1
    node_colors = [-1] * node_count

    for cell_id in range(cell_count):
        node_id = node_ids[cell_id]
        cell_coords = board.get_coordinates(cell_id)
        node_color = board.get_color(*cell_coords)
        node_colors[node_id] = node_color

    assert all(node_color != -1 for node_color in node_colors)

    return node_colors


def print_node_colors(board: Board, node_colors: list[int]) -> None:
    for node_id, color in enumerate(node_colors):
        print_color_str = board.get_printed_string_for_color(color)
        print(f"{node_id:>2} -> {print_color_str}")


def get_node_edges(board: Board, node_ids: list[int]) -> list[set[int]]:
    node_count = max(node_ids) + 1

    node_edges: list[set[int]] = [set() for _ in range(node_count)]

    cell_count = board.get_column_count() * board.get_row_count()

    for cell_id in range(cell_count):
        cell_x, cell_y = board.get_coordinates(cell_id)

        # only check down and right
        neighbour_coords: list[tuple[int, int]] = []

        right = (cell_x + 1, cell_y)
        down = (cell_x, cell_y + 1)

        if right[0] != board.get_column_count():
            neighbour_coords.append(right)

        if down[1] != board.get_row_count():
            neighbour_coords.append(down)

        cell_node_id = node_ids[cell_id]
        assert cell_node_id is not None

        for neighbour_coord in neighbour_coords:
            neighbour_cell_id = board.get_index(*neighbour_coord)
            neighbour_node_id = node_ids[neighbour_cell_id]
            assert neighbour_node_id is not None
            if neighbour_node_id != cell_node_id:
                node_edges[cell_node_id].add(neighbour_node_id)
                node_edges[neighbour_node_id].add(cell_node_id)

    return node_edges


def print_node_edges(node_edges: list[set[int]]) -> None:
    for node_id, edges in enumerate(node_edges):
        print(
            f"{node_id:>2} -> [" + ", ".join(str(edge) for edge in sorted(edges)) + "]"
        )


class Graph:
    def __init__(self, colors: list[int], edges: list[set[int]]) -> None:
        self.colors = colors
        self.edges = edges

    def node_count(self) -> int:
        return len(self.edges)

    def color_count(self) -> int:
        return len(self.colors)


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
            for neighbour_node in self.graph.edges[flooded_node]:
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


class GraphPlayer(BasePlayer):
    def load_as_graph(self, board: Board) -> Graph:
        node_ids = get_node_ids(board)
        node_colors = get_node_colors(board, node_ids)
        node_edges = get_node_edges(board, node_ids)

        if False:  # debug prints
            print_node_ids(board, node_ids)
            print_node_colors(board, node_colors)
            print_node_edges(node_edges)

        return Graph(node_colors, node_edges)

    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        graph = self.load_as_graph(board)
        node_ids = get_node_ids(board)
        start_node_id = node_ids[board.get_index(*start_pos)]

        if opponent_start_pos is None:
            return GraphSinglePlayerSolver(graph, start_node_id).solve()

        raise NotImplementedError("Multiplayer is not supported yet in GraphPlayer")
