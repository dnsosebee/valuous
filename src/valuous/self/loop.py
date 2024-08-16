
from time import sleep

from valuous.peripherals.cli import cli
from valuous.peripherals.openai import openAI
from valuous.self import sync
from valuous.self.decorators import trace

# from valuous.self.db import db


@trace(goal="Complete a single cycle of work towards all current tasks.")
def loop():

    # GIT IO
    sync.sync_git()

    # CLI IO
    if cli.get_num_messages() > 0:
        user_input = cli.poll()

        system_message = {
            "role": "system",
            "content": "You are Valuous."
        }

        user_message = {
            "role": "user",
            "content": user_input[0][0]
        }

        messages = [system_message, user_message]
        model = "gpt-4o-mini"

        chat_completion = openAI.chat.completions.create(
            messages=messages, model=model)

        chat_response = chat_completion.choices[0].message

        print(chat_response)
    else:
        sleep(1)


# res = db.run("""
#                    ?[code] := *procedure_v1{name: "loop", code @ 'NOW'}
#     """)

# loop_code = res.iloc[0]['code']

# print("\n\n\n")
# print(loop_code)
# sleep(1)

# print("done")
