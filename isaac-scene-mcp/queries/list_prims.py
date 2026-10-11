import json
import omni.usd

PREFIX = """__PREFIX__"""
MAX_DEPTH = int("""__MAX_DEPTH__""")
LIMIT = int("""__LIMIT__""")

stage = omni.usd.get_context().get_stage()
rows = []
for prim in stage.Traverse():
    path = str(prim.GetPath())
    if PREFIX and not path.startswith(PREFIX):
        continue
    depth = path.count("/")
    if depth > MAX_DEPTH:
        continue
    rows.append({"path": path, "type": prim.GetTypeName(), "depth": depth})
    if len(rows) >= LIMIT:
        break
print(json.dumps({"count": len(rows), "prims": rows}, indent=2))
