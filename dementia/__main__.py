from pathlib import Path
from sys import argv, stderr


def main() -> None:
    match argv[1:]:
        case [file]:
            run(Path(file).read_text())

        case _:
            print("Usage: dementia <program file>", file=stderr)
            raise SystemExit(1)


Instruction = tuple[str, int]
Bytecode = list[Instruction]


def build_bytecode(code: str) -> Bytecode:
    """
    Build bytecode for a Brainfuck program.

    This returns a list of tuples in the format of (instruction, amount),
    meaning "do this instruction this amount of times". Instructions may
    be one of the following:

        +      ("+", amount)  - will not be omitted in favor of a negative amount here
        >      (">", amount)  < will not be omitted in favor of a negative amount here
        ,      (",", 1)
        .      (".", 1)
        [-]    ("clear", 1)
        [-<+>] ("transfer", distance from current cell to target cell)
    """

    code_ptr = 0
    pass_1: Bytecode = []

    max_code_ptr = len(code)
    while code_ptr < max_code_ptr:
        cmd = code[code_ptr]

        if cmd in "+-":
            code_ptr, amount = sum_repeatable_commands(code, code_ptr, "+", "-")
            pass_1.append(("+", amount))

        elif cmd in "><":
            code_ptr, amount = sum_repeatable_commands(code, code_ptr, ">", "<")
            pass_1.append((">", amount))

        elif code[code_ptr : code_ptr + 3] in ("[-]", "[+]"):
            code_ptr += 2
            pass_1.append(("clear", 1))

        elif cmd in "[],.":
            pass_1.append((cmd, 1))

        code_ptr += 1

    pass_2: Bytecode = []
    i = 0
    while i < len(pass_1):
        match pass_1[i : i + 6]:
            case [
                ("[", _),
                ("-", 1),
                ("<", left),
                ("+", 1),
                (">", right),
                ("]", _),
            ] if left == right:
                pass_2.append(("move", -left))
                i += 5

            case [
                ("[", _),
                ("-", 1),
                (">", left),
                ("+", 1),
                ("<", right),
                ("]", _),
            ] if left == right:
                pass_2.append(("move", left))
                i += 5

            case _:
                pass_2.append(pass_1[i])
        i += 1

    return pass_2


def sum_repeatable_commands(
    code: str,
    code_ptr: int,
    positive: str,
    negative: str,
) -> tuple[int, int]:
    amount = 0

    while code[code_ptr] in (positive, negative):
        if code[code_ptr] == positive:
            amount += 1
        elif code[code_ptr] == negative:
            amount -= 1
        code_ptr += 1

    return (code_ptr - 1, amount)


def build_bracket_map(bytecode: Bytecode) -> dict[int, int]:
    """
    Build a bracket map.

    This returns a map from [ indices to their corresponding
    ] indices and vice versa. This means that for a program like:

        code:    [+++[-]++]
        indices: 0123456789

    the bracket map is:

        0 -> 9
        9 -> 0
        4 -> 6
        6 -> 4
    """

    bracket_map: dict[int, int] = {}
    stack: list[int] = []

    for i, (cmd, _) in enumerate(bytecode):
        if cmd == "[":
            stack.append(i)
        elif cmd == "]":
            start = stack.pop()
            end = i
            bracket_map[start] = end
            bracket_map[end] = start

    return bracket_map


def run(code: str) -> None:
    bytecode = build_bytecode(code)
    bracket_map = build_bracket_map(bytecode)

    tape: list[int] = [0] * 512
    tape_ptr = 0
    bytecode_ptr = 0

    max_bytecode_ptr = len(bytecode)
    while bytecode_ptr < max_bytecode_ptr:
        cmd, amount = bytecode[bytecode_ptr]

        if cmd == "+":
            tape[tape_ptr] = (tape[tape_ptr] + amount) % 256
        elif cmd == ">":
            tape_ptr += amount

        elif cmd == "clear":
            tape[tape_ptr] = 0

        elif cmd == "move":
            tape[tape_ptr + amount] += tape[tape_ptr]
            tape[tape_ptr] = 0

        elif (cmd == "[" and tape[tape_ptr] == 0) or (cmd == "]" and tape[tape_ptr] != 0):
            bytecode_ptr = bracket_map[bytecode_ptr]

        elif cmd == ",":
            tape[tape_ptr] = ord(input()[0])
        elif cmd == ".":
            print(chr(tape[tape_ptr]), end="")

        bytecode_ptr += 1


if __name__ == "__main__":
    main()
