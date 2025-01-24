

def read_procedure(name: str) -> str:
    sections = name.split(".")
    with open(f"src/valuous/{'/'.join(sections)}.py", "r") as f:
        procedure = f.read()
    return procedure
