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
    assistant_message = anthropic.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=max_tokens,
        stream=False,
        system=args.system,
        messages=args.messages,
        tools=as_anthropic_tools(args.tools),
        tool_choice="any",
    )

    tool_uses = [
        it for it in assistant_message.content if it.type == "tool_use"]

    if len(tool_uses) == 0:
        return {
            "assistant_message": assistant_message,
            "tool_message": None,
        }

    tool_use_responses = []
    for tool_use in tool_uses:
        tool_use_response = None
        try:
            tool_use_response = handle_tool_use(tool_use, args.tools)
        except Exception as e:
            tool_use_response = {
                "type": "tool_use",
                "tool_use_id": tool_use.id,
                "content": str(e),
                "is_error": True,
            }
        tool_use_responses.append(tool_use_response)

    user_message = {
        "type": "user",
        "content": tool_use_responses,
    }

    return {
        "assistant_message": assistant_message,
        "user_message": user_message,
    }


def handle_tool_use(tool_use: ToolUseBlockParam, tools: list[Tool]):
    matching_tool = next((tool for tool in tools if tool.name ==
                          tool_use.module + "." + tool_use.name), None)
    if matching_tool is None:
        raise ValueError("Tool not found")
    else:
        try:
            tool_input = matching_tool.input_class(**tool_use.input)
        except Exception as e:
            raise ValueError(f"Invalid input for tool: {str(e)}")
        else:
            try:
                matching_tool.func(tool_input)
            except Exception as e:
                raise ValueError(f"Error calling tool: {str(e)}")
            else:
                return {
                    "type": "tool_use",
                    "tool_use_id": tool_use.id,
                    "content": matching_tool.func(tool_input),
                }
