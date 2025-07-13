from pathlib import Path
from sys import argv, stderr

Instruction = tuple[str, int]
Bytecode = list[Instruction]


def build_bytecode(code: str) -> Bytecode:
    """
    Build bytecode for a Brainfuck program.

    This returns a list of tuples in the format of (op, amount),
    meaning "do this operation this amount of times". Instructions may
    be one of the following:

        +      ("+", amount)  - will not be omitted in favor of a negative amount here
        >      (">", amount)  < will not be omitted in favor of a negative amount here
        ,      (",", 1)
        .      (".", 1)
        [-]    ("clear", 1)
        [-<+>] ("transfer", distance from current cell to target cell)
        [->+<]<[<+>-] ("copy", distance from current cell to target cell)
    """

    pass_1 = parse_basic_instructions(code)
    return optimize_patterns(pass_1)


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


def parse_basic_instructions(code: str) -> Bytecode:
    code_ptr = 0
    bytecode: Bytecode = []

    max_code_ptr = len(code)
    while code_ptr < max_code_ptr:
        cmd = code[code_ptr]

        if cmd in "+-":
            code_ptr, amount = sum_repeatable_commands(code, code_ptr, "+", "-")
            bytecode.append(("+", amount))

        elif cmd in "><":
            code_ptr, amount = sum_repeatable_commands(code, code_ptr, ">", "<")
            bytecode.append((">", amount))

        elif cmd in "[],.":
            bytecode.append((cmd, 1))

        code_ptr += 1

    return bytecode


def optimize_patterns(bytecode: Bytecode) -> Bytecode:
    new_bytecode: Bytecode = []

    i = 0
    while i < len(bytecode):
        match bytecode[i : i + 6]:
            # [-] [+] Clear
            case [("[", _), ("+", _), ("]", _), *_]:
                new_bytecode.append(("clear", 1))
                i += 2

            # [-<+>] Transfer to the left
            case [
                ("[", _),
                ("+", -1),
                (">", left),
                ("+", 1),
                (">", right),
                ("]", _),
            ] if left == -right:
                new_bytecode.append(("transfer", left))
                i += 5

            case _:
                new_bytecode.append(bytecode[i])

        i += 1

    return new_bytecode


def build_python_code(bytecode: Bytecode) -> str:
    lines = [
        "tape = [0] * 512",
        "ptr = 0",
    ]

    indent = 0

    for op, amount in bytecode:
        line = ""

        if op == "+":
            line = f"tape[ptr] += {amount}"
        elif op == ">":
            line = f"ptr += {amount}"

        elif op == "[":
            lines.append("    " * indent + "while tape[ptr] != 0:")
            indent += 1
            continue
        elif op == "]":
            indent -= 1
            continue

        elif op == ",":
            line = "tape[ptr] = ord(input()[:1] or '\\0')"
        elif op == ".":
            line = "print(chr(tape[ptr]), end='')"

        elif op == "clear":
            line = "tape[ptr] = 0"

        elif op == "transfer":
            lines.append(f"{'    ' * indent}tape[ptr + {amount}] += tape[ptr]")
            lines.append(f"{'    ' * indent}tape[ptr] = 0")
            continue

        lines.append(f"{'    ' * indent}{line}")

    return "\n".join(lines)


def run(code: str) -> None:
    bytecode = build_bytecode(code)
    python = build_python_code(bytecode)
    exec(python)  # noqa: S102


def main() -> None:
    match argv[1:]:
        case [file]:
            run(Path(file).read_text())

        case _:
            print("Usage: dementia <program file>", file=stderr)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
