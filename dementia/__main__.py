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

    This returns a list of tuples in the format of (op, amount),
    meaning "do this operation this amount of times". Instructions may
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


def run(code: str) -> None:
    bytecode = build_bytecode(code)

    python = [
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
            python.append("    " * indent + "while tape[ptr] != 0:")
            indent += 1
            continue
        elif op == "]":
            indent -= 1
            continue

        elif op == ",":
            line = "tape[ptr] = ord(input()[0])"
        elif op == ".":
            line = "print(chr(tape[ptr]), end='')"

        elif op == "clear":
            line = "tape[ptr] = 0"

        elif op == "move":
            line = f"tape[ptr], tape[ptr + {amount}] = tape[ptr]"
            continue

        python.append(f"{'    ' * indent}{line}")

    exec("\n".join(python))  # noqa: S102


if __name__ == "__main__":
    main()
