import uuid
from functools import wraps
from typing import Any, Optional

from pydantic import BaseModel, Field


def trace_to_string(trace: 'Trace'):
    return f"{trace.data.module_name}.{trace.data.qualified_name} - {trace.data.goal}"


class TraceData(BaseModel):
    id: str
    module_name: str
    qualified_name: str
    goal: str
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
                goal="root",
                args=(),
                kwargs={},
                result=None
            ),
            active=True
        )
        self.head_trace = self.root_trace


trace_state = TraceState()


def trace(goal: str = "unknown"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parent = trace_state.head_trace

            new_trace = Trace(
                data=TraceData(
                    id=str(uuid.uuid4()),
                    module_name=func.__module__,
                    qualified_name=func.__qualname__,
                    goal=goal,
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
    print(f"{'  ' * indent}module: {t.data.module_name}, goal: {t.data.goal}")
    for child in t.children:
        print_trace(child, indent + 1)
