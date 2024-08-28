from time import sleep

from valuous.self.tool import ToolResponse


def wake_t() -> ToolResponse:
    return {"data": {}, "affordances": [nap_t]}


def nap_t() -> ToolResponse:
    """Sleep for five minutes, unless woken up by a notification."""
    print("nap_t")
    sleep(60 * 5)
    print("woke up")
    response = wake_t()
    response["redirect"] = {"tool": wake_t, "args": None}
    return response
