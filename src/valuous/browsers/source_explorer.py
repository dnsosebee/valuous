import inspect
from importlib import import_module

from pydantic import BaseModel

from valuous.self.tool import ToolResponse


class ExploreSourceArgs(BaseModel):
    module_name: str
    qualified_name: str


def explore_source_init() -> ToolResponse:
    return {
        "data": {},
        "affordances": [explore_source_t]
    }


def explore_source_t(args: ExploreSourceArgs) -> ToolResponse:
    """Explore the source code of a function or class within yourself. Args can come from the """
    try:
        # Import the module
        module = import_module(args.module_name)

        # Navigate to the object using the qualified name
        obj = module
        for part in args.qualified_name.split('.'):
            if part:  # Skip empty parts
                obj = getattr(obj, part)

        # Get the source code
        source = inspect.getsource(obj)

        return {"data": {"source": source}, "affordances": [explore_source_t]}
    except Exception as e:
        return {"data": {"source": f"Failed to get source code: {str(e)}"}, "affordances": [explore_source_t]}
