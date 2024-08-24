from typing import Literal, Type, TypedDict, Union

from anthropic.types.message_param import MessageParam
from anthropic.types.tool_use_block_param import ToolUseBlockParam
from pydantic import BaseModel

from valuous.peripherals.model_providers.anthropic import (anthropic,
                                                           as_anthropic_tools)
from valuous.self.tool import Tool

max_tokens = 1024


class InferArgs(BaseModel):
    messages: list[MessageParam]
    system: str
    tools: list[Tool]


def infer(args: InferArgs):

    tools = as_anthropic_tools(args.tools)

    print(tools)

    assistant_message = anthropic.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=max_tokens,
        stream=False,
        system=args.system,
        messages=args.messages,
        tools=tools,
        tool_choice={"type": "any"},
    )

    tool_uses = [
        it for it in assistant_message.content if it.type == "tool_use"]

    if len(tool_uses) == 0:
        return {
            "assistant_message": assistant_message,
            "tool_message": None,
        }

    interactions = []
    for tool_use in tool_uses:
        interactions.append(resolve_interaction(tool_use, args.tools))

    return {
        "assistant_message": assistant_message,
        "interactions": interactions,
    }


class SuccessInteraction(TypedDict):
    tool_use_id: str
    is_error: Literal[False]
    tool: Tool
    args: Type[BaseModel]


class FailureInteraction(TypedDict):
    tool_use_id: str
    is_error: Literal[True]
    exception: Exception


Interaction = Union[SuccessInteraction, FailureInteraction]


def resolve_interaction(tool_use: ToolUseBlockParam, tools: list[Tool]) -> Interaction:
    matching_tool = next((tool for tool in tools if tool.name ==
                          tool_use.module + "." + tool_use.name), None)
    if matching_tool is None:
        return {
            "tool_use_id": tool_use.id,
            "exception": ValueError("Tool not found"),
        }
    else:
        try:
            tool_input = matching_tool.input_class(**tool_use.input)
        except Exception as e:
            return {
                "tool_use_id": tool_use.id,
                "exception": ValueError(f"Invalid input for tool: {str(e)}"),
            }
        else:
            try:
                matching_tool.func(tool_input)
            except Exception as e:
                return {
                    "tool_use_id": tool_use.id,
                    "exception": ValueError(f"Error calling tool: {str(e)}"),
                }
            else:
                return {
                    "tool_use_id": tool_use.id,
                    "tool": matching_tool,
                    "args": tool_input,
                }

# tool_use_response = {
#     "type": "tool_use",
#     "tool_use_id": tool_use.id,
#     "content": str(e),
#     "is_error": True,
# }
