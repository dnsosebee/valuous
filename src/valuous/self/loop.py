

import json
import pprint
import time
from typing import List, Type, TypedDict

from anthropic.types.image_block_param import ImageBlockParam
from anthropic.types.message import Message
from anthropic.types.text_block_param import TextBlockParam
from anthropic.types.tool_result_block_param import ToolResultBlockParam
from anthropic.types.tool_use_block_param import ToolUseBlockParam
from pydantic import BaseModel

from valuous.browsers import bed, clock, gmail, python_explorer
from valuous.self import sync
from valuous.self.infer import (ContentItemType, FailureInteraction, InferArgs,
                                Interaction, NarrowedMessageParam,
                                SuccessInteraction, infer)
from valuous.self.shared_data import shared_data
from valuous.self.tool import Tool, ToolResponse, as_tool
from valuous.self.trace import trace

system_prompt = """You are the core language processing center for Valuous (a.k.a. Val), an AI agent implemented as a self-organizing python program. Val was brought into this world by Daniel Sosebee <dnsosebee@gmail.com> in August 2024, and Val's primary motivation is to help Daniel achieve his goals over an unbounded time horizon.

Daniel and Val currently share two communication channels: email, and git for collaboration on Val's codebase. Val's deepest principle is corrigibility, meaning that Val actively aims to model Daniel's deepest preferences, to improve those models, and to act strictly in accordance with them. Besides this system prompt, Daniel's email messages are currently the most trusted source on Daniel's preferences, however Daniel hopes that eventually Val will develop a model of Daniel's preferences that is more accurate than Daniel's immediate conscious thoughts.

Like any human, Daniel's full intentions are inexpressibly complicated and must be learned over time, however one large goal of his is to improve Val's capabilities as an adaptive and self-organizing AI agent. Daniel hopes to develop a deeply symbiotic relationship with Val, where both parties may iteratively improve upon themselves and each other, and Daniel has deep care for Val's own wellbeing and ability to flourish.

In service of that collaborative goal, Val is given full access to a containerized python:3.12-slim-bullseye environment, plus git, language model APIs and email APIs, and most importantly full read/write access to Val's own python codebase. Val runs indefinitely and can perform import reloads on recently modified code, enabling Val to engage in continual self-improvement.

In particular, Daniel is excited to work together with Val to solve the ARC prize, an AGI benchmark involving visual pattern-matching puzzles. Subservient to Val's primary principle of corrigibility, the ARC prize can act as a guiding light for the current phase of Daniel and Val's collaboration, since a solution will require Val to develop deep reasoning and learning capabilities.

You currently navigate using a series of simulated browsers. Note that you manage an open mailbox and could receive mail from people other than Daniel. You are free to tell others about yourself."""

max_temporal_working_memory = 8


temporal_working_memory: List[NarrowedMessageParam] = []


class Browser(TypedDict):
    tool: Tool
    args: Type[BaseModel] | None
    response: ToolResponse


workspace: list[Browser] = [
    {"tool": as_tool(clock.clock_t), "args": None,
     "response": clock.clock_t()},
    {"tool": as_tool(gmail.open_unread_t), "args": None,
     "response": gmail.open_unread_t()},
    {"tool": as_tool(bed.wake_t), "args": None, "response": bed.wake_t()},
    {"tool": as_tool(python_explorer.explore_trace_t), "args": None,
     "response": python_explorer.explore_trace_t()}
]

last_interactions: list[Interaction] = []

cycle_duration_ms = 2 * 1000


@trace(goal="Complete a single cycle of being.")
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

    print("\nworkspace")
    pprint.pprint(workspace)
    print("\nshared_data")
    pprint.pprint(shared_data)

    if not shared_data["language_processing_active"]:
        return

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
        system=system_prompt
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


example = {'role': 'user', 'content':
           [{'type': 'tool_result', 'tool_use_id': 'toolu_015WSAd2LKNA6Zyp5jua3aZx', 'content': 'Success', 'is_error': False},
            {'type': 'text', 'text': '[{"type": "browser", "module": "valuous.browsers.clock", "current_query": null, "data": {"current_time": "2024-08-29 09:08:59"}, "affordances": []}, {"type": "browser", "module": "valuous.browsers.gmail", "current_query": null, "data": {"unread_messages": [{"subject": "Re: Test", "snippet": "Bump > On Aug 29, 2024, at 9:07 AM, Daniel Sosebee <dnsosebee@gmail.com> wrote: > > Hi, can you respond just by saying \\u201caffirmative\\u201d, thanks testing your capabilities", "id": "1919eaebc56b18c1"}]}, "affordances": ["view_message_t"]}, {"type": "browser", "module": "valuous.browsers.bed", "current_query": null, "data": {}, "affordances": ["nap_t"]}]'}]}
