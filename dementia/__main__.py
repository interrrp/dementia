from dataclasses import dataclass
from pathlib import Path
from sys import argv, stderr


# fmt: off
@dataclass(frozen=True)
class IncCell:
    amount: int

@dataclass(frozen=True)
class IncPtr:
    amount: int

@dataclass(frozen=True)
class Transfer:
    distance: int

class StartLoop: ...
class EndLoop: ...
class Input: ...
class Output: ...
class Clear: ...
# fmt: on


Instruction = IncCell | IncPtr | StartLoop | EndLoop | Transfer | Input | Output | Clear
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
            bytecode.append(IncCell(amount))

        elif cmd in "><":
            code_ptr, amount = sum_repeatable_commands(code, code_ptr, ">", "<")
            bytecode.append(IncPtr(amount))

        elif cmd == "[":
            bytecode.append(StartLoop())
        elif cmd == "]":
            bytecode.append(EndLoop())
        elif cmd == ",":
            bytecode.append(Input())
        elif cmd == ".":
            bytecode.append(Output())

        code_ptr += 1

    return bytecode


def optimize_patterns(bytecode: Bytecode) -> Bytecode:
    new_bytecode: Bytecode = []

    i = 0
    while i < len(bytecode):
        match bytecode[i:]:
            # [-] [+] Clear
            case [StartLoop(), IncCell(_), EndLoop(), *_]:
                new_bytecode.append(Clear())
                i += 3

            # [-<+>] Transfer to the left
            case [
                StartLoop(),
                IncCell(-1),
                IncPtr(left),
                IncCell(1),
                IncPtr(right),
                EndLoop(),
                *_,
            ] if left == -right:
                new_bytecode.append(Transfer(left))
                i += 6

            case _:
                new_bytecode.append(bytecode[i])
                i += 1

    return new_bytecode


def build_python_code(bytecode: Bytecode) -> str:  # noqa: C901
    lines = [
        "tape = [0] * 512",
        "ptr = 0",
    ]

    indent = 0

    def emit(line: str) -> None:
        lines.append(f"{'    ' * indent}{line}")

    for op in bytecode:
        match op:
            case IncCell(amount):
                emit(f"tape[ptr] = (tape[ptr] + {amount}) % 256")
            case IncPtr(amount):
                emit(f"ptr += {amount}")

            case StartLoop():
                emit("while tape[ptr] != 0:")
                indent += 1
            case EndLoop():
                indent -= 1

            case Input():
                emit("tape[ptr] = ord(input()[:1] or '\\0')")
            case Output():
                emit("print(chr(tape[ptr]), end='')")

            case Clear():
                emit("tape[ptr] = 0")

            case Transfer(distance):
                emit(f"tape[ptr + {distance}] += tape[ptr]")
                emit("tape[ptr] = 0")

    return "\n".join(lines)


def run(code: str) -> None:
    bytecode = build_bytecode(code)
    python = build_python_code(bytecode)
    exec(python)  # noqa: S102


def main() -> None:
    try:
        run(Path(argv[1]).read_text())
    except IndexError:
        fail("Usage: dementia <program file>")
    except FileNotFoundError:
        fail(f"{argv[1]} does not exist")


def fail(msg: str) -> None:
    print(msg, file=stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
