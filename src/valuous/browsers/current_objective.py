
from pydantic import BaseModel

from valuous.self.tool import ToolResponse

objective_data = {
    "objective": None,
    "complete": False,
    "root": False,
}


def set_new_objective(objective: str, is_root: bool):
    global objective_data
    objective_data["objective"] = objective
    objective_data["complete"] = False
    objective_data["root"] = is_root


def view_root_objective_t() -> ToolResponse:
    global objective_data
    return {"data": objective_data, "affordances": [
        set_new_objective_t,
    ]}


def view_objective_t() -> ToolResponse:
    global objective_data
    return {"data": objective_data, "affordances": [
        set_new_objective_t,
        mark_objective_complete_t
    ]}


class SetNewObjectiveArgs(BaseModel):
    objective: str


def set_new_objective_t(args: SetNewObjectiveArgs) -> ToolResponse:
    """Pushes a new objective onto your stack."""
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
