from flood.board import Board
from flood.players.graph.types import BitSet


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


def get_node_neighbours(board: Board, node_ids: list[int]) -> list[set[int]]:
    node_count = max(node_ids) + 1

    node_neighbours: list[set[int]] = [set() for _ in range(node_count)]

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
                node_neighbours[cell_node_id].add(neighbour_node_id)
                node_neighbours[neighbour_node_id].add(cell_node_id)

    return node_neighbours


def print_node_neighbours(node_neighbours: list[set[int]]) -> None:
    for node_id, neighbours in enumerate(node_neighbours):
        print(
            f"{node_id:>2} -> ["
            + ", ".join(str(neighbour) for neighbour in sorted(neighbours))
            + "]"
        )


class Graph:
    def __init__(self, colors: list[int], neighbours: list[set[int]]) -> None:
        # node id -> bitset of neighbour node ids
        self.neighbours: list[BitSet] = [
            BitSet.from_set(node_neighbours) for node_neighbours in neighbours
        ]

        # color id -> bitset of node ids with that color
        self.colors = [BitSet(0) for _ in range(max(colors) + 1)]
        for index, color in enumerate(colors):
            self.colors[color] = BitSet(self.colors[color] | 1 << index)

    def node_count(self) -> int:
        return len(self.neighbours)

    def color_count(self) -> int:
        return len(self.colors)

    def get_color(self, node: int) -> int:
        # This is slow and should not be used for searching

        if node not in range(self.node_count()):
            raise ValueError("Invalid node id")

        for color, color_bitset in enumerate(self.colors):
            if (1 << node) & color_bitset:
                return color

        # Unreachable
        raise NotImplementedError

    def get_neighbour_list(self, node: int) -> list[int]:
        # This is slow and should not be used for searching
        return [n for n in range(self.node_count()) if self.neighbours[node] & (1 << n)]
