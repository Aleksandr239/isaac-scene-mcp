import json
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics

PRIM_PATH = """__PRIM_PATH__"""

stage = omni.usd.get_context().get_stage()
prim = stage.GetPrimAtPath(PRIM_PATH)
if not prim or not prim.IsValid():
    raise RuntimeError(f"Prim not found: {PRIM_PATH}")

info = {
    "path": str(prim.GetPath()),
    "type": prim.GetTypeName(),
    "children": [{"path": str(c.GetPath()), "type": c.GetTypeName()} for c in prim.GetChildren()],
    "has_collision": prim.HasAPI(UsdPhysics.CollisionAPI),
    "has_articulation_root": prim.HasAPI(UsdPhysics.ArticulationRootAPI),
    "translate": None,
    "orient_xyz_deg": None,
    "scale": None,
    "world_bbox": None,
}

xform = UsdGeom.Xformable(prim)
if xform:
    for op in xform.GetOrderedXformOps():
        t = op.GetOpType()
        val = op.Get()
        if val is None:
            continue
        if t == UsdGeom.XformOp.TypeTranslate:
            info["translate"] = [float(val[0]), float(val[1]), float(val[2])]
        elif t == UsdGeom.XformOp.TypeScale:
            info["scale"] = [float(val[0]), float(val[1]), float(val[2])]
        elif t in (UsdGeom.XformOp.TypeRotateXYZ, UsdGeom.XformOp.TypeRotateXZY,
                   UsdGeom.XformOp.TypeRotateYXZ, UsdGeom.XformOp.TypeRotateYZX,
                   UsdGeom.XformOp.TypeRotateZXY, UsdGeom.XformOp.TypeRotateZYX):
            info["orient_xyz_deg"] = [float(val[0]), float(val[1]), float(val[2])]

try:
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    box = cache.ComputeWorldBound(prim).ComputeAlignedBox()
    mn, mx = box.GetMin(), box.GetMax()
    info["world_bbox"] = {
        "min": [float(mn[0]), float(mn[1]), float(mn[2])],
        "max": [float(mx[0]), float(mx[1]), float(mx[2])],
    }
except Exception as exc:
    info["world_bbox_error"] = str(exc)

print(json.dumps(info, indent=2))
