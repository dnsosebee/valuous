from valuous.example_module.example_submodule import (invalid_tool_function,
                                                      tool_function)
from valuous.self.tool import as_tool, execute_tool


def test_get_tool():
    tool = as_tool(tool_function)
    assert tool.module == "valuous.example_module.example_submodule"
    assert tool.name == "tool_function"
    assert tool.description == "Returns a message based on the input"
    assert tool.input_class.__qualname__ == "TestPeripheralArgs"
    assert tool.func == tool_function

    instance = {"name": "foo"}
    res = execute_tool(tool, instance)

    assert res == "TestPeripheral received: name='foo'"


def test_get_tool_invalid():
    try:
        as_tool(invalid_tool_function)
        assert False
    except ValueError as e:
        assert str(
            e) == "Argument of invalid_tool_function must be a Pydantic model."
