import json
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics

PREFIX = """__PREFIX__"""
MIN_SIZE = float("""__MIN_SIZE__""")
LIMIT = int("""__LIMIT__""")

stage = omni.usd.get_context().get_stage()
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
rows = []

for prim in stage.Traverse():
    if not prim.IsA(UsdGeom.Mesh):
        continue
    path = str(prim.GetPath())
    if PREFIX and not path.startswith(PREFIX):
        continue
    # skip looks/materials branches by name
    if any(part in ("Looks", "Materials", "Render") for part in path.split("/")):
        continue
    try:
        box = cache.ComputeWorldBound(prim).ComputeAlignedBox()
        mn, mx = box.GetMin(), box.GetMax()
        size = [float(mx[i] - mn[i]) for i in range(3)]
        if max(size) < MIN_SIZE:
            continue
        rows.append(
            {
                "path": path,
                "collision": prim.HasAPI(UsdPhysics.CollisionAPI),
                "min": [float(mn[0]), float(mn[1]), float(mn[2])],
                "max": [float(mx[0]), float(mx[1]), float(mx[2])],
                "size": size,
            }
        )
    except Exception:
        continue
    if len(rows) >= LIMIT:
        break

# largest first
rows.sort(key=lambda r: max(r["size"]), reverse=True)
print(json.dumps({"count": len(rows), "meshes": rows}, indent=2))
