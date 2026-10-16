# C Terminal Tutor

An offline, beginner-friendly C course for your Fedora terminal. Seven interactive lessons cover hello world, variables, decisions, loops, functions, arrays, and pointers. Each includes a quiz and a real C editing exercise checked by compiling and running it.

## Run on Fedora

Install the tools once:

```bash
sudo dnf install python3 gcc nano
```

From this directory, start the tutor:

```bash
python3 ctutor.py
```

Choose lesson 1. Keep the tutor open and use a second terminal to edit the exercise file at the path it prints. Return to the tutor and press `r` to compile and check your work. Compiler errors are part of learning: fix the first reported error and retry.

Exercises and progress are saved in `~/.local/share/ctutor` (or `$XDG_DATA_HOME/ctutor` when set). Existing exercises are preserved when you revisit a lesson. No Python packages, accounts, or network connection are needed after installation.

The tutor checks program output; it does not grade your coding style or prove that you used the requested technique. Read each exercise and try the requested approach. Your compiled C code runs with your normal user permissions.

## Check the examples

```bash
python3 ctutor.py --self-test
```

This compiles all seven examples with C17 and compiler warnings enabled and checks their output. To compile an exercise yourself:

```bash
gcc -std=c17 -Wall -Wextra -pedantic ~/.local/share/ctutor/lesson1.c -o /tmp/my-c-lesson
/tmp/my-c-lesson
```
