
from valuous.self.shared_data import shared_data
from valuous.self.tool import ToolResponse


def wake_t() -> ToolResponse:
    return {"data": {}, "affordances": [nap_t]}


def nap_t() -> ToolResponse:
    """Sleep until the next notification occurs, for example, a new email."""
    shared_data["active"] = False
    response = wake_t()
    response["redirect"] = {"tool": wake_t, "args": None}
    return response
