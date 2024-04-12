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
        graph = self.load_as_graph(board)
        node_ids = get_node_ids(board)
        start_node_id = node_ids[board.get_index(*start_pos)]

        if opponent_start_pos is None:
            return GraphSinglePlayerSolver(graph, start_node_id).solve()

        raise NotImplementedError("Multiplayer is not supported yet in GraphPlayer")
