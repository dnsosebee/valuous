

from valuous.self import sync
from valuous.self.decorators import trace

# from valuous.self.db import db


@trace(goal="Complete a single cycle of work towards all current tasks.")
def loop():

    # GIT IO
    sync.sync_git()


# res = db.run("""
#                    ?[code] := *procedure_v1{name: "loop", code @ 'NOW'}
#     """)

# loop_code = res.iloc[0]['code']

# print("\n\n\n")
# print(loop_code)
# sleep(1)

# print("done")
