from anthropic import Anthropic
from anthropic.types.tool_param import ToolParam

from valuous.self.tool import Tool
from valuous.settings import settings

anthropic = Anthropic(api_key=settings.anthropic_api_key)


def as_anthropic_tools(tools: list[Tool]) -> list[ToolParam]:
    return [
        ToolParam(
            name=tool.module + "." + tool.name,
            description=tool.description,
            input_schema=tool.input_class.model_json_schema(),
        )
        for tool in tools
    ]
