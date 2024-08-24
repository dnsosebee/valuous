from anthropic import Anthropic
from anthropic.types.tool_param import ToolParam

from valuous.self.tool import Tool
from valuous.settings import settings

anthropic = Anthropic(api_key=settings.anthropic_api_key)

simple_json_schema = {
    "type": "object",
    "properties": {
    }
}


def as_anthropic_tools(tools: list[Tool]) -> list[ToolParam]:
    return [
        ToolParam(
            name=as_anthropic_tool_name(tool),
            description=tool.description,
            input_schema=tool.input_class.model_json_schema(
            ) if tool.input_class else simple_json_schema
        )
        for tool in tools
    ]


def as_anthropic_tool_name(tool: Tool) -> str:
    return (tool.module + "." + tool.name).replace(".", "-")
