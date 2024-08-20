import inspect
from typing import Callable

from pydantic import BaseModel


class Tool(BaseModel):
    module: str
    name: str
    description: str
    input_class: type[BaseModel]
    func: Callable

    model_config = {
        "arbitrary_types_allowed": True
    }


def as_tool(func: Callable) -> Tool:
    module_name = func.__module__
    function_name = func.__name__

    docstring = inspect.getdoc(func) or "No description available."

    signature = inspect.signature(func)
    params = list(signature.parameters.values())

    if len(params) != 1:
        raise ValueError(
            f"Function {function_name} must have exactly one argument.")

    param = params[0]

    if not (inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel)):
        raise ValueError(
            f"Argument of {function_name} must be a Pydantic model.")

    input_class = param.annotation

    return Tool(module=module_name, name=function_name, description=docstring, input_class=input_class, func=func)


def validate_args(tool: Tool, input: dict):
    return tool.input_class(**input)


def execute_tool(tool: Tool, instance: dict):
    args = validate_args(tool, instance)
    return tool.func(args)
