# src/valuous/self/main.py - This is the execution entrypoint to valuous, executed by the environment on startup.

from valuous.procedures.read_procedure import read_procedure


def read_procedure(name: str) -> str:
    sections = name.split(".")
    with open(f"src/valuous/{'/'.join(sections)}.py", "r") as f:
        procedure = f.read()
    return procedure


def setup():
    while True:
        loop = read_procedure("self.loop")
        exec(loop)
        exec(loop)
