
from pycozo.client import Client

from valuous.peripherals.memory import logger

db = Client('rocksdb', 'valuous' + '.db')

# initialize DB
schema = [
    """:create procedure_v1 {name: String, ts: Validity default 'ASSERT' => code: String}""",
    """:create cli_input_v1 {id: Uuid default rand_uuid_v4(), ts: Validity default 'ASSERT' => message: String}""",
    """:create cli_output_v1 {id: Uuid default rand_uuid_v4(), ts: Validity default 'ASSERT' => message: String}""",
]
for s in schema:
    try:
        db.run(s)
    except Exception as e:
        if e.code == 'eval::stored_relation_conflict':
            logger.warning(f'Schema already exists: {s}')
        else:
            raise

# load setup and loop procedures
# for name in ['loop']:
#     with open(f'src/agent/procedures/{name}.py', 'r') as f:
#         code = f.read()

#     db.run("""
#             ?[name, code] <- [[$name, $code]]

#             :put procedure_v1 {name, code}
#             """, {'name': name, 'code': code})
