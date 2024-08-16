
import logging

logging.basicConfig(filename='valuous.log', level=logging.DEBUG)
# res = db.run(
#     ":replace trace_node {uid: String, ts: Validity default 'ASSERT' => record: String, source: String, prev_event: String, parent_event: String,}")
# print(type(res))

logger = logging.getLogger(__name__)
