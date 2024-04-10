from __future__ import annotations
from copy import copy
import random
from typing import Optional

BASH_COLOR_CODES = [
    "30",  # black
    "31",  # red
    "32",  # green
    "33",  # yellow
    "34",  # blue
    "35",  # magenta
    "36",  # cyan
    "37",  # white
    "90",  # gray
    "91",  # light red
    "92",  # light green
    "93",  # light yellow
    "94",  # light blue
    "95",  # light magenta
    "96",  # light cyan
    "97",  # light white
]


class Board:
    def __init__(self, fields: list[int], rows: int) -> None:
        assert fields
        assert rows in range(100)
        assert len(fields) % rows == 0

        # Don't use these fields directly, implementation may change
        self.__fields = fields
        self.__rows = rows

    @classmethod
    def random(cls, rows: int, columns: int, colors: int) -> Board:
        fields: list[int] = [
            random.randint(0, colors - 1) for _ in range(rows * columns)
        ]
        return Board(fields, rows)

    def get_column_count(self) -> int:
        return len(self.__fields) // self.get_row_count()

    def get_row_count(self) -> int:
        return self.__rows

    def get_index(self, x: int, y: int) -> int:
        return y * self.get_row_count() + x

    def get_coordinates(self, pos: int) -> tuple[int, int]:
        x = pos % self.get_row_count()
        y = pos // self.get_row_count()
        return x, y

    def get_color(self, x: int, y: int) -> int:
        index = self.get_index(x, y)
        return self.__fields[index]

    def get_remaining_colors(self) -> set[int]:
        return set(self.__fields)

    def get_printed_string_for_color(self, color: int) -> str:
        try:
            color_code = BASH_COLOR_CODES[color]
        except IndexError:
            return f"{color:>2}"

        return f"\033[{color_code}m██\033[0m"

    def print(self) -> None:
        for y in range(self.get_row_count()):
            for x in range(self.get_column_count()):
                color = self.get_color(x, y)
                printed = self.get_printed_string_for_color(color)
                print(printed, end="")
            print()

    def get_flooded_cells(self, start_pos: tuple[int, int]) -> set[int]:
        explored: set[tuple[int, int]] = set()
        unexplored = {start_pos}

        start_x, start_y = start_pos
        flood_color = self.get_color(start_x, start_y)

        while True:
            try:
                pos = unexplored.pop()
            except KeyError:
                break

            x, y = pos

            if x not in range(self.get_column_count()):
                # falls of board left or right
                continue

            if y not in range(self.get_row_count()):
                # falls of board top or bottom
                continue

            if self.get_color(x, y) != flood_color:
                # wrong color
                continue

            left = (x - 1, y)
            right = (x + 1, y)
            up = (x, y - 1)
            down = (x, y + 1)

            explored.add(pos)
            unexplored.update([left, right, up, down])

            # prevent going back and forth
            unexplored -= explored

        return {self.get_index(x, y) for x, y in explored}

    def count_flooded_cells(self, start_pos: tuple[int, int]) -> int:
        flooded = self.get_flooded_cells(start_pos)
        return len(flooded)

    def do_move(self, start_pos: tuple[int, int], color: int) -> Board:
        flooded = self.get_flooded_cells(start_pos)

        fields = copy(self.__fields)
        for index in flooded:
            fields[index] = color

        return Board(fields, self.get_row_count())

    def is_solved(self) -> bool:
        # This applies to single player only.
        return len(self.get_remaining_colors()) == 1

    def get_valid_moves(
        self, start_pos: tuple[int, int], opponent_start_pos: Optional[tuple[int, int]]
    ) -> set[int]:
        colors = self.get_remaining_colors()
        current_color = self.get_color(*start_pos)
        colors = colors - {current_color}

        if opponent_start_pos is not None:
            opponent_color = self.get_color(*opponent_start_pos)
            colors = colors - {opponent_color}

        return colors
