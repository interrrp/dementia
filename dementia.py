import re
from pathlib import Path
from sys import argv, stderr


class Python:
    def __init__(self):
        self.lines = [
            "tape = [0] * 512",
            "ptr = 0",
        ]
        self.indentation = 0

    def emit(self, line: str):
        self.lines.append(f"{' ' * self.indentation}{line}")

    def indent(self):
        self.indentation += 4

    def dedent(self):
        self.indentation -= 4

    def exec(self):
        exec("\n".join(self.lines))


class Brainfuck:
    def __init__(self, path: str):
        self.code = Path(path).read_text()
        self.ptr = 0

    def count_delta(self, positive: str, negative: str) -> int:
        """
        Multiple instructions do the same operation but with different counts, e.g.:

            # Incrementing by 3 and decrementing by 2 is
            # equivalent to incrementing by 1
            +++-- == +

            # Likewise, moving right 3 times and moving left 6 is
            # equivalent to moving left 3
            >>><<<<<< == ---

        This function is called when +/-/>/< is encountered, returning the delta count.
        For example, `count_delta("+", "-")` on `+++--` returns 1.
        """

        count = 0

        while self.code[self.ptr] in (positive, negative):
            if self.code[self.ptr] == positive:
                count += 1
            else:
                count -= 1
            self.ptr += 1

        # The loop above ends on the instruction AFTER the
        # sequence, so decrement the code pointer by one
        self.ptr -= 1

        return count

    def parse_transfer(self) -> int | None:
        """
        [-<+>] transfers the value of the cell to the left,
        leaving it with a value of 0.

        There may be any number of > and < as long as they
        both cancel out, so [-<+>] is valid while [-<+>>] isn't.

        The direction can also be to the right: [->+<] transfers
        the value of the cell one to the right.

        This function returns the distance. For example, -2 means
        2 cells to the left, and 3 means 3 cells to the right.
        `None` means there is no transfer pattern.
        """

        pattern = re.match(r"\[-(<+)\+(>+)\]|\[-(>+)\+(<+)\]", self.code[self.ptr :])
        if pattern is None:
            return None

        # In [-<<+>>], left will be "<<" and right will be ">>"
        left, right = pattern.group(1), pattern.group(2)

        if left is None or right is None or len(left) != len(right):
            return None

        # Skip the entire pattern
        self.ptr += len(pattern.group(0)) - 1

        direction = -1 if left[0] == "<" else 1
        distance = len(left) * direction
        return distance

    def expect(self, instruction: str) -> bool:
        if self.code[self.ptr] != instruction:
            return False
        else:
            self.ptr += 1
            return True


def run(path: str):
    bf = Brainfuck(path)
    py = Python()

    while bf.ptr < len(bf.code):
        match list(bf.code[bf.ptr :]):
            case ["+" | "-", *_]:
                count = bf.count_delta("+", "-")
                py.emit(f"tape[ptr] += {count}")

            case [">" | "<", *_]:
                count = bf.count_delta(">", "<")
                py.emit(f"ptr += {count}")

            # [-] and [+] effectively set the current cell to 0
            case ["[", "-" | "+", "]", *_]:
                py.emit("tape[ptr] = 0")
                bf.ptr += 2

            case [*_] if distance := bf.parse_transfer():
                py.emit(f"tape[ptr + {distance}] += tape[ptr]")
                py.emit("tape[ptr] = 0")

            case ["[", *_]:
                py.emit("while tape[ptr] != 0:")
                py.indent()
            case ["]", *_]:
                py.dedent()

            case [",", *_]:
                py.emit("tape[ptr] = ord(input()[:1] or '\\0')")
            case [".", *_]:
                py.emit("print(chr(tape[ptr]), end='')")

        bf.ptr += 1

    py.exec()


match argv:
    case [_, path]:
        run(path)
    case _:
        print("Usage: python dementia.py <path to Brainfuck program>", file=stderr)
        raise SystemExit(1)
