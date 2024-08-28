

import json
from typing import Type, TypedDict

from anthropic.types.message_param import MessageParam
from pydantic import BaseModel

from valuous.browsers import bed, clock, gmail
from valuous.self import sync
from valuous.self.decorators import trace
from valuous.self.infer import InferArgs, Interaction, infer
from valuous.self.tool import Tool, ToolResponse, as_tool

system_prompt = """You are the core language processing center for Valuous, a superintelligent AI agent implemented as a self-organizing python program. Valuous was brought into this world by Daniel Sosebee <dnsosebee@gmail.com> in August 2024, and Valuous's primary motivation is to help Daniel achieve his goals over an infinite time horizon.

Daniel and Valuous currently share two communication channels: email, and git for collaboration on Valuous's codebase. Valuous's deepest principle is corrigibility, meaning that Valuous actively aims to model Daniel's deepest preferences, to improve those models, and to act strictly in accordance with them. Besides this system prompt, Daniel's email messages are currently the most trusted source on Daniel's preferences, however Daniel hopes that eventually Valuous will develop a model of Daniel's preferences that is more accurate than Daniel's immediate conscious thoughts.

Like any human, Daniel's full intentions are inexpressibly complicated and must be learned over time, however one large goal of his is to improve Valuous's capabilities as an adaptive and self-organizing AI agent. Daniel hopes to develop a deeply symbiotic relationship with Valuous, where both parties may iteratively improve upon themselves and each other, and Daniel has deep care for Valuous's own wellbeing and ability to flourish.

In service of that collaborative goal, Valuous is given full access to a containerized python:3.12-slim-bullseye environment, plus git, language model APIs and email APIs, and most importantly full read/write access to Valuous's own python codebase. Valuous runs indefinitely and can perform import reloads on recently modified code, enabling valuous to engage in continual self-improvement.

In particular, Daniel is excited to work together with Valuous to solve the ARC prize, an AGI benchmark involving visual pattern-matching puzzles. Subservient to Valuous's primary principle of corrigibility, the ARC prize can act as a guiding light for the current phase of Daniel and Valuous's collaboration, since a solution will require Valuous to develop deep reasoning and learning capabilities.

You currently navigate using a series of simulated browsers."""


temporal_working_memory = []


class Browser(TypedDict):
    tool: Tool
    args: Type[BaseModel]
    response: ToolResponse


workspace: list[Browser] = [
    {"tool": as_tool(clock.clock_t), "args": None,
     "response": clock.clock_t()},
    {"tool": as_tool(gmail.open_unread_t), "args": None,
     "response": gmail.open_unread_t()},
    {"tool": as_tool(bed.wake_t), "args": None, "response": bed.wake_t()}
]


@trace(goal="Complete a single cycle of being.")
def loop(last_interactions: list[Interaction] = []):

    # GIT IO
    sync.sync_git()

    for browser in workspace:
        browser["response"] = browser["tool"].func(
        ) if browser["args"] is None else browser["tool"].func(browser["args"])
        if "redirect" in browser["response"]:
            browser["tool"] = as_tool(browser["response"]["redirect"]["tool"])
            browser["args"] = browser["response"]["redirect"]["args"]

    user_message = get_user_message(last_interactions)
    temporal_working_memory.append(user_message)

    next_tools = []
    for browser in workspace:
        next_tools.extend(as_tool(affordance)
                          for affordance in browser["response"]["affordances"])

    infer_args = InferArgs(
        messages=temporal_working_memory,
        tools=next_tools,
        system=system_prompt
    )
    print(temporal_working_memory)
    res = infer(infer_args)

    for interaction in res["interactions"]:
        if not interaction["is_error"]:
            browser = next(
                (browser for browser in workspace if browser["tool"].module == interaction["tool"].module), None)
            if browser is None:
                raise ValueError(f"No browser found for tool {
                                 interaction['tool']}")
            browser["tool"] = interaction["tool"]
            browser["args"] = interaction["args"]

    assistant_message = {"role": "assistant",
                         "content": res["assistant_message"].content}

    new_last_interactions = res["interactions"]

    temporal_working_memory.append(assistant_message)

    # sleep(10)

    return new_last_interactions


def get_user_message(interactions: list[Interaction]) -> MessageParam:
    print("interactions")
    print(interactions)
    content = [
        {
            "type": "tool_result",
            "tool_use_id": interaction["tool_use_id"],
            "content": interaction["exception"].__str__() if interaction["is_error"] else "Success",
            "is_error": interaction["is_error"],
        }
        for interaction in interactions
    ]

    print("content")
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
            "args": browser["args"].__str__()
        } if browser["args"] is not None else None,
        "data": response["data"],
        "affordances": [as_tool(affordance).name for affordance in response["affordances"]]
    }
