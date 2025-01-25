from valuous.self.tool import ToolResponse
from valuous.self.trace import trace_state, trace_to_string


def view_stack_t() -> ToolResponse:
    global active_trace

    data = {
        "stack": []
    }

    ancestor_trace = trace_state.head_trace

    while ancestor_trace.parent is not None:
        data["stack"].insert(0, trace_to_string(ancestor_trace))
        ancestor_trace = ancestor_trace.parent

    data["stack"].insert(0, trace_to_string(ancestor_trace))

    return {"data": data, "affordances": []}
