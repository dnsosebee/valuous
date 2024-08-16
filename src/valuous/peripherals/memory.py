
# import logging

# logging.basicConfig(filename='valuous.log', level=logging.DEBUG)


# logger = logging.getLogger(__name__)

# # res = db.run(
# #     ":replace trace_node {uid: String, ts: Validity default 'ASSERT' => record: String, source: String, prev_event: String, parent_event: String,}")
# # print(type(res))

from valuous.self.decorators import trace


@trace("remember")
def remember(message: str):
    return message
