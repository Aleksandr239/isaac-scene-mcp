import json
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics

ROBOT_PATH = """__ROBOT_PATH__"""

stage = omni.usd.get_context().get_stage()
prim = stage.GetPrimAtPath(ROBOT_PATH)
if not prim or not prim.IsValid():
    # try fuzzy find
    hits = []
    for p in stage.Traverse():
        path = str(p.GetPath()).lower()
        if "nova_carter" in path or "carter" in path or "jetbot" in path:
            hits.append(str(p.GetPath()))
    raise RuntimeError(
        f"Robot prim not found at {ROBOT_PATH}. Candidates: {hits[:20]}"
    )

snap = {
    "path": str(prim.GetPath()),
    "type": prim.GetTypeName(),
    "has_articulation_root": prim.HasAPI(UsdPhysics.ArticulationRootAPI),
    "world_pose": None,
    "joints": [],
    "drive_joints": [],
}

try:
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    box = cache.ComputeWorldBound(prim).ComputeAlignedBox()
    mn, mx = box.GetMin(), box.GetMax()
    center = [(mn[i] + mx[i]) * 0.5 for i in range(3)]
    snap["world_bbox"] = {
        "min": [float(mn[0]), float(mn[1]), float(mn[2])],
        "max": [float(mx[0]), float(mx[1]), float(mx[2])],
        "center": [float(c) for c in center],
    }
except Exception as exc:
    snap["world_bbox_error"] = str(exc)

# local translate of root
xform = UsdGeom.Xformable(prim)
if xform:
    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            val = op.Get()
            if val is not None:
                snap["translate"] = [float(val[0]), float(val[1]), float(val[2])]

for child in stage.Traverse():
    path = str(child.GetPath())
    if not path.startswith(str(prim.GetPath())):
        continue
    if child.IsA(UsdPhysics.RevoluteJoint) or child.GetTypeName() in (
        "PhysicsRevoluteJoint",
        "PhysicsPrismaticJoint",
    ):
        name = child.GetName()
        entry = {"path": path, "name": name, "type": child.GetTypeName()}
        snap["joints"].append(entry)
        if "wheel" in name.lower() and "caster" not in name.lower():
            snap["drive_joints"].append(name)

# live articulation state if available
try:
    from isaacsim.core.prims import SingleArticulation

    art = SingleArticulation(ROBOT_PATH)
    art.initialize()
    snap["dof_names"] = list(art.dof_names) if hasattr(art, "dof_names") else None
    try:
        pos = art.get_joint_positions()
        vel = art.get_joint_velocities()
        snap["joint_positions"] = pos.tolist() if hasattr(pos, "tolist") else list(pos)
        snap["joint_velocities"] = vel.tolist() if hasattr(vel, "tolist") else list(vel)
    except Exception as exc:
        snap["joint_state_error"] = str(exc)
except Exception as exc:
    snap["articulation_api_note"] = str(exc)

print(json.dumps(snap, indent=2))
