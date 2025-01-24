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

    class Config:
        frozen = True  # Makes the Pydantic model immutable


def create_trace(
    module_name: str,
    qualified_name: str,
    goal: str,
    args: Any,
    kwargs: dict,
    parent: Optional['Trace'] = None
) -> Trace:
    """Pure function to create a new trace"""
    return Trace(
        data=TraceData(
            id=str(uuid.uuid4()),
            module_name=module_name,
            qualified_name=qualified_name,
            goal=goal,
            args=args,
            kwargs=kwargs,
            result=None
        ),
        active=True,
        parent=parent,
        children=[]
    )


def add_result_to_trace(trace: Trace, result: Any) -> Trace:
    """Pure function to add a result to a trace"""
    return Trace(
        data=TraceData(**{**trace.data.model_dump(), "result": result}),
        children=trace.children,
        active=False,
        parent=trace.parent
    )


def add_child_to_trace(parent: Trace, child: Trace) -> Trace:
    """Pure function to add a child to a trace"""
    return Trace(
        data=parent.data,
        children=[*parent.children, child],
        active=parent.active,
        parent=parent.parent
    )


# Global pointers to immutable traces
root_trace = create_trace(
    module_name="root",
    qualified_name="root",
    goal="root",
    args=(),
    kwargs={},
    parent=None
)

head_trace = root_trace


def trace(goal: str = "unknown"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global head_trace

            # Create new trace
            current = create_trace(
                module_name=func.__module__,
                qualified_name=func.__qualname__,
                goal=goal,
                args=args,
                kwargs=kwargs,
                parent=head_trace
            )

            # Run function
            result = func(*args, **kwargs)

            # Create new immutable traces
            completed = add_result_to_trace(current, result)
            new_head = add_child_to_trace(head_trace, completed)

            # Update global pointer
            head_trace = new_head

            return result

        return wrapper
    return decorator
