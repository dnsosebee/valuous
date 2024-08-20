from pydantic import BaseModel


class TestPeripheralArgs(BaseModel):
    name: str


def tool_function(args: TestPeripheralArgs) -> str:
    """Returns a message based on the input"""

    return f"TestPeripheral received: {args}"


def invalid_tool_function(args: str) -> str:
    """Returns a message based on the input - invalid because it doesn't take a Pydantic model"""

    return f"TestPeripheral received: {args}"
