
from typing import Callable

from pydantic import BaseModel

from valuous.self.tool import ToolResponse
from valuous.self.trace import trace

objective_data = {
    "objective": None,
    "complete": False,
    "root": True,
}


@trace(lambda objective, is_root: f"set new objective: {objective}" + (
    " (root objective is perpetual)" if is_root else ""))
def set_new_objective(objective: str, is_root: bool):
    global objective_data
    objective_data["objective"] = objective
    objective_data["complete"] = False
    objective_data["root"] = is_root


def view_objective_t() -> ToolResponse:
    global objective_data
    affordances: list[Callable[..., ToolResponse]] = [
        set_new_objective_t,
    ]
    if not objective_data["root"]:
        affordances.append(mark_objective_complete_t)
    return {"data": objective_data, "affordances": affordances}


class SetNewObjectiveArgs(BaseModel):
    objective: str


def set_new_objective_t(args: SetNewObjectiveArgs) -> ToolResponse:
    """Pushes a new objective onto your stack. Use this if you have a task you'd like to remember as you work towards executing it."""
    set_new_objective(args.objective, False)
    response = view_objective_t()
    response["redirect"] = {"tool": view_objective_t, "args": None}
    return response


def mark_objective_complete_t() -> ToolResponse:
    """Marks the current objective as complete, and pops it off the stack."""
    global objective_data
    objective_data["complete"] = True

    response = view_objective_t()
    response["redirect"] = {"tool": view_objective_t, "args": None}
    return response
