import uuid
from functools import wraps
from typing import Any, Optional

from pydantic import BaseModel, Field


def trace_to_string(trace: 'Trace'):
    return f"<Trace module='{trace.data.module_name}' qualified_name='{trace.data.qualified_name}' rendered='{trace.data.rendered}'>"


class TraceData(BaseModel):
    id: str
    module_name: str
    qualified_name: str
    rendered: str
    args: Any
    kwargs: dict
    result: Any


class Trace(BaseModel):
    data: TraceData
    children: list['Trace'] = Field(default_factory=list)
    active: bool
    parent: Optional['Trace'] = None


class TraceState:
    def __init__(self):
        self.root_trace = Trace(
            data=TraceData(
                id="root",
                module_name="root",
                qualified_name="root",
                rendered="root",
                args=(),
                kwargs={},
                result=None
            ),
            active=True
        )
        self.head_trace = self.root_trace


trace_state = TraceState()


def trace(render=None):
    """
    Decorator that traces function execution.

    Args:
        render: Optional function that takes (*args, **kwargs) and returns a string description
               of what the function call is trying to achieve. If None, uses the function name.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Default render function uses the function name
            render_fn = render if render else lambda *a, **kw: f"Calling {
                func.__name__}"
            description = render_fn(*args, **kwargs)

            parent = trace_state.head_trace

            new_trace = Trace(
                data=TraceData(
                    id=str(uuid.uuid4()),
                    module_name=func.__module__,
                    qualified_name=func.__qualname__,
                    rendered=description,  # Using the rendered description instead of static goal
                    args=args,
                    kwargs=kwargs,
                    result=None
                ),
                active=True,
                parent=parent
            )

            trace_state.head_trace = new_trace
            parent.children.append(trace_state.head_trace)

            try:
                result = func(*args, **kwargs)
                trace_state.head_trace.data.result = result
                return result
            finally:
                trace_state.head_trace = parent
                trace_state.head_trace.active = False
        return wrapper
    return decorator


def print_trace(t: Trace, indent: int = 0):
    print(f"{'  ' * indent}{trace_to_string(t)}")
    for child in t.children:
        print_trace(child, indent + 1)
