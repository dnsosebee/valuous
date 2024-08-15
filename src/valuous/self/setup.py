# src/valuous/self/main.py - This is the execution entrypoint to valuous, executed by the environment on startup.


from valuous.self.loop import loop
from valuous.self.procedure import procedure


@procedure
def setup():
    while True:
        loop()
