# Dementia

A blazingly fast Brainfuck interpreter written in Python.

## Usage

1. Install [Python](https://python.org/).
2. Clone the repository.
3. `python dementia.py <path to Brainfuck program>`

Example programs are provided in the [programs](programs) directory.

## How it works

It goes through the Brainfuck code and builds Python code based on it. Certain
patterns get optimized:

| Pattern    | Python           |
| ---------- | ---------------- |
| `+++++--`  | `tape[ptr] += 3` |
| `>>>>><<`  | `ptr += 3`       |
| `[-]`      | `tape[ptr] = 0`  |
| `[-<<+>>]` | `transfer(-2)`   |

## PyPy

Since Brainfuck programs are naturally dominated by tight loops, PyPy's JIT offers a 27x speed boost on [`programs/mandelbrot.b`](programs/mandelbrot.b) compared to CPython on my machine (3s vs 1m27s).

## License

This project is licensed under the [MIT license](LICENSE).
