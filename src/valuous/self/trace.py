import uuid
from functools import wraps
from typing import Any, Optional

from pydantic import BaseModel


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
    children: list['Trace'] = []
    active: bool
    parent: Optional['Trace'] = None


root_trace = Trace(data=TraceData(id="root", module_name="root", qualified_name="root",
                   goal="root", args=(), kwargs={}, result=None), active=True)

head_trace = root_trace


def trace(goal: str = "unknown"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global head_trace, root_trace
            parent = head_trace

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

            head_trace = new_trace

            try:
                result = func(*args, **kwargs)
                head_trace.data.result = result
                return result
            finally:
                # Clean up: mark as inactive, add to parent's children, restore head
                head_trace.active = False
                parent.children.append(head_trace)
                head_trace = parent

        return wrapper
    return decorator
