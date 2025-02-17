# CURRENTLY NOT IN USE


from pycozo.client import Client

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
        if 'eval::stored_relation_conflict' in str(e):
            print(f'Schema already exists: {s}')
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


# res = db.run("""
#                    ?[code] := *procedure_v1{name: "loop", code @ 'NOW'}
#     """)

# loop_code = res.iloc[0]['code']

# print("\n\n\n")
# print(loop_code)
# sleep(1)

# print("done")
