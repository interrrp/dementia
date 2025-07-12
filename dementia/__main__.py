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
    meaning "do this instruction this amount of times".

    Only the instructions +-<> have varying amounts. [],. are fixed to an
    amount of 1, regardless of whether they are repeated multiple times in a row.
    """

    code_ptr = 0
    instructions: Bytecode = []

    max_code_ptr = len(code)
    while code_ptr < max_code_ptr:
        initial_code_ptr = code_ptr
        cmd = code[code_ptr]

        if cmd in "+-<>":
            cmd = code[initial_code_ptr]
            code_ptr = initial_code_ptr
            while code_ptr + 1 < len(code) and code[code_ptr + 1] == cmd:
                code_ptr += 1
            amount = code_ptr - initial_code_ptr + 1
            instructions.append((cmd, amount))
        elif cmd in "[],.":
            instructions.append((cmd, 1))

        code_ptr += 1

    return instructions


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

    for i, c in enumerate(bytecode):
        if c[0] == "[":
            stack.append(i)
        elif c[0] == "]":
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
        match bytecode[bytecode_ptr]:
            case ("+", amount):
                tape[tape_ptr] += amount
            case ("-", amount):
                tape[tape_ptr] -= amount
            case (">", amount):
                tape_ptr += amount
            case ("<", amount):
                tape_ptr -= amount
            case ("[", _) if tape[tape_ptr] == 0:
                bytecode_ptr = bracket_map[bytecode_ptr]
            case ("]", _) if tape[tape_ptr] != 0:
                bytecode_ptr = bracket_map[bytecode_ptr]
            case (",", _):
                pass
            case (".", _):
                print(chr(tape[tape_ptr]), end="", flush=True)
            case _:
                pass
        bytecode_ptr += 1


if __name__ == "__main__":
    main()
