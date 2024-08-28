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


browser_prefix = "valuous-browser-"


def as_anthropic_tool_name(tool: Tool) -> str:
    # Combine module and name, replace dots with underscores, and limit to 64 characters
    combined_name = (tool.module + "_" + tool.name).replace(".", "-")
    # Ensure the name only contains alphanumeric characters and underscores
    sanitized_name = ''.join(
        c for c in combined_name if c.isalnum() or c == '_')
    # Truncate to 64 characters if necessary

    # remove browser prefix if it exists
    if sanitized_name.startswith(browser_prefix):
        sanitized_name = sanitized_name[len(browser_prefix):]

    return sanitized_name[:64]
