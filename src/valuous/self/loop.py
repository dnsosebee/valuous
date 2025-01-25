

import json
import pprint
import time
from typing import Callable, List, Type, TypedDict

from anthropic.types.image_block_param import ImageBlockParam
from anthropic.types.message import Message
from anthropic.types.text_block_param import TextBlockParam
from anthropic.types.tool_result_block_param import ToolResultBlockParam
from anthropic.types.tool_use_block_param import ToolUseBlockParam
from pydantic import BaseModel

from valuous.browsers import (bed, clock, current_objective, gmail,
                              source_explorer, stack_view)
from valuous.self import sync
from valuous.self.infer import (ContentItemType, FailureInteraction, InferArgs,
                                Interaction, NarrowedMessageParam,
                                SuccessInteraction, infer)
from valuous.self.shared_data import shared_data
from valuous.self.system_prompts import system_prompt_simple
from valuous.self.tool import Tool, ToolResponse, as_tool
from valuous.self.trace import trace

# FOR CURRENT TESTING: please try creating an objective called "look at my stack trace and email it to dnsosebee@gmail.com."

max_temporal_working_memory = 8


temporal_working_memory: List[NarrowedMessageParam] = []


class Browser(TypedDict):
    tool: Tool
    args: Type[BaseModel] | None
    response: ToolResponse


def create_browser(tool: Callable[..., ToolResponse], args: Type[BaseModel] | None = None) -> Browser:
    return {"tool": as_tool(tool), "args": args, "response": tool()}


workspace: list[Browser] = [
    create_browser(clock.clock_t),
    create_browser(stack_view.view_stack_t),
    create_browser(source_explorer.explore_source_init),
    create_browser(current_objective.view_objective_t),
    create_browser(gmail.open_unread_t),
    create_browser(bed.wake_t),
]

last_interactions: list[Interaction] = []

cycle_duration_ms = 2 * 1000


@trace(lambda objective, is_root: f"complete the following objective: {objective}" + (
    " (root objective is perpetual)" if is_root else ""))
def complete_objective(objective: str, is_root: bool):
    current_objective.set_new_objective(objective, is_root=is_root)
    while True:
        loop()
        outgoing_objective = current_objective.objective_data["objective"]
        if outgoing_objective != objective:
            complete_objective(outgoing_objective, is_root=False)
            current_objective.set_new_objective(objective, is_root=is_root)
        if current_objective.objective_data["complete"]:
            break


def loop():

    remaining_cycle_time = shared_data["last_cycle_ms"] + \
        cycle_duration_ms - time.time() * 1000
    if remaining_cycle_time > 0:
        time.sleep(remaining_cycle_time / 1000)
    shared_data["last_cycle_ms"] = time.time() * 1000

    # GIT IO
    sync.sync_git()

    for browser in workspace:
        browser["response"] = browser["tool"].func(
        ) if browser["args"] is None else browser["tool"].func(browser["args"])
        if "redirect" in browser["response"]:
            browser["tool"] = as_tool(browser["response"]["redirect"]["tool"])
            browser["args"] = browser["response"]["redirect"]["args"]

    if not shared_data["language_processing_active"]:
        return

    print("\n\n\n\n\n")
    print("\nworkspace")
    pprint.pprint(workspace)
    print("\n\n\n\n\n")

    user_message = get_user_message(last_interactions)
    temporal_working_memory.append(user_message)

    if len(temporal_working_memory) >= max_temporal_working_memory:
        temporal_working_memory[:] = temporal_working_memory[
            len(temporal_working_memory) - max_temporal_working_memory:]

    while temporal_working_memory[0]["role"] != "user":
        temporal_working_memory.pop(0)

    first_message = temporal_working_memory[0]
    while first_message['content'][0]['type'] == "tool_result":
        first_message['content'].pop(0)

    next_tools = []
    for browser in workspace:
        next_tools.extend(as_tool(affordance)
                          for affordance in browser["response"]["affordances"])

    infer_args = InferArgs(
        messages=temporal_working_memory,
        tools=next_tools,
        system=system_prompt_simple
    )
    res = infer(infer_args)

    last_interactions[:] = res["interactions"]

    print("last_interactions")
    print(last_interactions)

    for interaction in last_interactions:
        match interaction:
            case SuccessInteraction(tool=tool, args=args):
                browser = next(
                    (browser for browser in workspace if browser["tool"].module == tool.module), None)
                if browser is None:
                    raise ValueError(f"No browser found for tool {tool}")
                browser["tool"] = tool
                browser["args"] = args

    assistant_message = convert_to_message_param(res["assistant_message"])

    temporal_working_memory.append(assistant_message)


def convert_to_message_param(message: Message) -> NarrowedMessageParam:
    return NarrowedMessageParam(
        role=message.role,
        content=[
            TextBlockParam(
                **content_block.model_dump(mode='json', exclude_unset=True))
            if content_block.type == 'text' else
            ImageBlockParam(
                **content_block.model_dump(mode='json', exclude_unset=True))
            if content_block.type == 'image' else
            ToolUseBlockParam(
                **content_block.model_dump(mode='json', exclude_unset=True))
            if content_block.type == 'tool_use' else
            ToolResultBlockParam(
                **content_block.model_dump(mode='json', exclude_unset=True))
            for content_block in message.content
        ]
    )


def get_user_message(interactions: list[Interaction]) -> NarrowedMessageParam:

    content: list[ContentItemType] = []

    for interaction in interactions:
        match interaction:
            case FailureInteraction(tool_use_id=tool_use_id, exception=exception):
                content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": str(exception),
                    "is_error": True,
                })
            case SuccessInteraction(tool_use_id=tool_use_id):
                content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": "Success",
                    "is_error": False,
                })

    workspace_perception = [render_browser_window(
        browser) for browser in workspace]

    content.append({
        "type": "text",
        "text": json.dumps(workspace_perception)
    })
    return {
        "role": "user",
        "content": content
    }


def render_browser_window(browser: Browser) -> dict:
    response = browser["response"]
    return {
        "type": "browser",
        "module": browser["tool"].module,
        "current_query": {
            "name": browser["tool"].name,
            "args": str(browser["args"])
        } if browser["args"] is not None else None,
        "data": response["data"],
        "affordances": [as_tool(affordance).name for affordance in response["affordances"]]
    }
