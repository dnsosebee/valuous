# src/valuous/self/main.py - This is the execution entrypoint to valuous, executed by the environment on startup.


from valuous.self.decorators import trace
from valuous.self.loop import loop


def setup():
    start_loop()


@trace(goal="Be a corrigible agent. Provide long-horizon value to the user by continuously attempting to understand the user's long-term preferences and adapting yourself to maximally help them. Improve yourself as needed in the process.")
def start_loop():
    while True:
        loop()
