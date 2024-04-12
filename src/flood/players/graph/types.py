from __future__ import annotations
from typing import Iterator


class SolutionFound(Exception):
    def __init__(self, moves: list[int]) -> None:
        self.moves = moves


class BitSet(int):
    def count(self) -> int:
        return bin(self).count("1")

    @classmethod
    def from_set(self, int_set: set[int]) -> BitSet:
        value = 0
        for i in int_set:
            value |= 1 << i
        return BitSet(value)

    def to_set(self) -> set[int]:
        binary = bin(self)[2:]
        return {i for i, bit in enumerate(binary[::-1]) if bit == "1"}

    def __iter__(self) -> Iterator[int]:
        return iter(self.to_set())
