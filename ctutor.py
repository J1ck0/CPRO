#!/usr/bin/env python3
"""A small, offline terminal course in C. Requires Python 3 and GCC."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

LESSONS = [
    ("Hello, C", "Every C program starts in main(). stdio.h declares printf. Statements end with a semicolon.\\n inside a string prints a newline.",
     '#include <stdio.h>\nint main(void) {\n    printf("Hello, C!\\n");\n    return 0;\n}\n',
     "Which function is the entry point?", "main", "Change the message to Hello, Fedora!", "Hello, Fedora!\n"),
    ("Variables and arithmetic", "int stores whole numbers. %d formats an int in printf. Arithmetic uses +, -, *, / and %. Integer division discards the fractional part.",
     '#include <stdio.h>\nint main(void) {\n    int apples = 7;\n    int baskets = 2;\n    printf("%d\\n", apples / baskets);\n    return 0;\n}\n',
     "What is 7 / 2 with integer operands?", "3", "Print the remainder of 7 divided by 2 instead.", "1\n"),
    ("Decisions", "if runs a block when its condition is true; else handles the other case. == compares values; = assigns a value. Braces group statements.",
     '#include <stdio.h>\nint main(void) {\n    int score = 65;\n    if (score >= 50) {\n        puts("pass");\n    } else {\n        puts("retry");\n    }\n    return 0;\n}\n',
     "Which operator tests equality?", "==", "Change score so this program prints retry.", "retry\n"),
    ("Loops", "A for loop has initialization, a condition checked before each iteration, and an update. i++ adds one. Watch bounds to avoid an extra iteration.",
     '#include <stdio.h>\nint main(void) {\n    for (int i = 1; i <= 3; i++) {\n        printf("%d\\n", i);\n    }\n    return 0;\n}\n',
     "How many times does this loop run?", "3", "Extend the loop to print the numbers 1 through 5, one per line.", "1\n2\n3\n4\n5\n"),
    ("Functions", "Functions name reusable work. Parameters receive inputs; return sends a result back. Define a function before its first call or declare its prototype.",
     '#include <stdio.h>\nint square(int n) {\n    return n * n;\n}\nint main(void) {\n    printf("%d\\n", square(3));\n    return 0;\n}\n',
     "What does square(3) return?", "9", "Use square to print the square of 7.", "49\n"),
    ("Arrays and strings", "An array stores several values. Indexing starts at zero. A C string is a char array ending in a zero byte. Never access outside an array's bounds.",
     '#include <stdio.h>\nint main(void) {\n    int values[] = {10, 20, 30};\n    printf("%d\\n", values[0]);\n    return 0;\n}\n',
     "What is the index of the first element?", "0", "Print the last element of values.", "30\n"),
    ("Pointers", "A pointer holds an address. &x gets x's address. *p reads or writes the object at p. Only dereference valid pointers to live objects.",
     '#include <stdio.h>\nint main(void) {\n    int number = 10;\n    int *p = &number;\n    *p = 20;\n    printf("%d\\n", number);\n    return 0;\n}\n',
     "Which operator gets a variable's address?", "&", "Change number to 42 through the pointer and print it.", "42\n"),
]


def compile_run(source):
    if not shutil.which("gcc"):
        print("GCC is missing. On Fedora: sudo dnf install gcc")
        return None
    with tempfile.TemporaryDirectory(prefix="ctutor-") as folder:
        executable = Path(folder) / "program"
        try:
            result = subprocess.run(["gcc", "-std=c17", "-Wall", "-Wextra", "-pedantic", str(source.resolve()), "-o", str(executable)], capture_output=True, text=True, timeout=20)
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode:
                print("Compilation failed. Read the first compiler error, edit, then try again.")
                return None
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=3)
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode:
                print(f"Program exited with status {result.returncode}.")
                return None
            return result.stdout
        except subprocess.TimeoutExpired:
            print("Time limit reached. Check for an infinite loop.")
            return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="compile and check all lesson examples")
    args = parser.parse_args()
    if args.self_test:
        expected = ["Hello, C!\n", "3\n", "pass\n", "1\n2\n3\n", "9\n", "10\n", "20\n"]
        with tempfile.TemporaryDirectory() as folder:
            for i, lesson in enumerate(LESSONS):
                source = Path(folder) / "example.c"
                source.write_text(lesson[2])
                if compile_run(source) != expected[i]:
                    raise SystemExit(f"Lesson {i + 1} failed")
                print(f"Lesson {i + 1}: passed")
        return
    root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "ctutor"
    root.mkdir(parents=True, exist_ok=True)
    progress = root / "progress.json"
    try:
        done = set(json.loads(progress.read_text()))
    except (OSError, ValueError, TypeError):
        done = set()
    print("\nC TERMINAL TUTOR — learn by changing real programs")
    print("Your exercises and progress live in", root)
    while True:
        print("\n" + "\n".join(f"{i + 1}. {'[done]' if i + 1 in done else '[    ]'} {lesson[0]}" for i, lesson in enumerate(LESSONS)))
        choice = input("\nChoose a lesson (1–7), or q to quit: ").strip()
        if choice.lower() == "q":
            return
        if choice not in [str(i) for i in range(1, len(LESSONS) + 1)]:
            continue
        n = int(choice)
        title, explanation, code, question, answer, task, expected = LESSONS[n - 1]
        print(f"\n{title}\n\n{explanation}\n\n{code}")
        print("Quick quiz:", question)
        print("Correct!" if input("> ").strip().lower() == answer else f"Answer: {answer}")
        source = root / f"lesson{n}.c"
        if not source.exists():
            source.write_text(code)
        print("\nExercise:", task)
        print("Open a second terminal and edit:", source)
        print(f"For example: nano {source}")
        while True:
            action = input("[r] compile/run/check, [s] show your code, [b] back: ").strip().lower()
            if action == "b":
                break
            if action == "s":
                print(source.read_text())
            if action == "r":
                output = compile_run(source)
                if output is not None:
                    print("Output:\n" + output, end="" if output.endswith("\n") else "\n")
                    if output == expected:
                        print("Exercise passed! Explain to yourself why your change works.")
                        done.add(n)
                        progress.write_text(json.dumps(sorted(done)))
                        break
                    print("Keep going! Expected output:", repr(expected))


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nSee you next time!")
