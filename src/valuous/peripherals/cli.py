import threading
from collections import deque
from datetime import datetime


class CLIInterface:
    def __init__(self):
        self.messages = deque()
        self.lock = threading.Lock()
        self.running = True
        self.input_thread = threading.Thread(target=self._input_loop)
        self.input_thread.start()

    def _input_loop(self):
        while self.running:
            user_input = input("> ")
            with self.lock:
                self.messages.appendleft((user_input, datetime.now()))

    def stop(self):
        self.running = False
        self.input_thread.join()

    def get_num_messages(self):
        with self.lock:
            return len(self.messages)

    def poll(self, n=1):
        with self.lock:
            return [self.messages.popleft() for _ in range(min(n, len(self.messages)))]


cli = CLIInterface()
