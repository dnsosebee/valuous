

from valuous.self.tool import ToolResponse
from valuous.self.trace import trace, trace_state, trace_to_string

valuous_sender = "Valuous <valuous@gmail.com>"

active_trace = trace_state.root_trace


def jump_to_head_trace_t() -> ToolResponse:
    global active_trace
    active_trace = trace_state.head_trace
    return explore_trace_t()


@trace(lambda: f"exploring trace: {trace_to_string(active_trace)}")
def explore_trace_t() -> ToolResponse:
    global active_trace

    data = {
        "stack": []
    }

    ancestor_trace = active_trace

    while ancestor_trace.parent is not None:
        data["stack"].insert(0, trace_to_string(ancestor_trace))
        ancestor_trace = ancestor_trace.parent

    data["stack"].insert(0, trace_to_string(ancestor_trace))

    return {"data": data, "affordances": [jump_to_head_trace_t]}
