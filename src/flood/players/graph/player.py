from typing import Optional
from flood.board import Board
from flood.players.base import BasePlayer
from flood.players.graph.graph import (
    get_node_colors,
    get_node_ids,
    get_node_neighbours,
    print_node_colors,
    print_node_ids,
    print_node_neighbours,
    Graph,
)
from flood.players.graph.solver import GraphSinglePlayerSolver


class GraphPlayer(BasePlayer):
    def __init__(self) -> None:
        self.next_solution_moves: Optional[list[int]] = None

    def load_as_graph(self, board: Board) -> Graph:
        node_ids = get_node_ids(board)
        node_colors = get_node_colors(board, node_ids)
        node_neighbours = get_node_neighbours(board, node_ids)

        if False:  # debug prints
            print_node_ids(board, node_ids)
            print_node_colors(board, node_colors)
            print_node_neighbours(node_neighbours)

        return Graph(node_colors, node_neighbours)

    def get_best_move(
        self,
        board: Board,
        start_pos: tuple[int, int],
        opponent_start_pos: tuple[int, int] | None,
        timeout: float | None = None,
    ) -> int:
        if self.next_solution_moves is not None:
            move = self.next_solution_moves[0]
            self.next_solution_moves = self.next_solution_moves[1:]
            return move

        graph = self.load_as_graph(board)
        node_ids = get_node_ids(board)
        start_node_id = node_ids[board.get_index(*start_pos)]

        if opponent_start_pos is None:
            solution_moves = GraphSinglePlayerSolver(graph, start_node_id).solve()
            self.next_solution_moves = solution_moves[1:]
            return solution_moves[0]

        raise NotImplementedError("Multiplayer is not supported yet in GraphPlayer")
