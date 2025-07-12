# Dementia

A blazingly fast Brainfuck interpreter written in Python.

## Usage

1. Install [Python](https://python.org/) if you haven't already.
2. Clone the repository.
3. `python -m dementia <path to program>`

Example programs are provided in the [programs](programs) directory.

## Optimizations

"How is it so fast?" you may ask. Well, optimizations, of course. How else?

### 1. Process Brainfuck into IR

Identifies common patterns:

| Pattern    | IR            |
| ---------- | ------------- |
| `+++++--`  | `+ 3`         |
| `>>>>><<`  | `> 3`         |
| `[-]`      | `clear`       |
| `[-<<+>>]` | `transfer -2` |

### 2. Build Python code

Transforms the IR into Python code.

```py
# +++ (+ 3) gets transformed into this:
tape[ptr] += 3

# Similarly, >>> (> 3) gets transformed into this:
ptr += 3

# etc...
```

### 3. Execute Python code

Execute the generated Python code using `exec`.

### 4. Use PyPy (optional, 27x speed boost)

The performance difference between running this on CPython compared to PyPy is quite huge. On [mandelbrot.b](programs/mandelbrot.b), PyPy offered a 27x speed boost (1m27s vs 3s!).

## License

This project is licensed under the [MIT](LICENSE) license.
