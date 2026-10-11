import json
import omni.usd
from pxr import UsdGeom

stage = omni.usd.get_context().get_stage()
playing = False
try:
    import omni.timeline

    playing = bool(omni.timeline.get_timeline_interface().is_playing())
except Exception:
    pass

dp = stage.GetDefaultPrim() if stage else None
meta = {
    "up_axis": UsdGeom.GetStageUpAxis(stage) if stage else None,
    "meters_per_unit": UsdGeom.GetStageMetersPerUnit(stage) if stage else None,
    "default_prim": str(dp.GetPath()) if dp else None,
    "playing": playing,
    "root_layer": stage.GetRootLayer().identifier if stage else None,
    "world_children": [],
}
if stage:
    world = stage.GetPrimAtPath("/World")
    if world and world.IsValid():
        meta["world_children"] = [
            {"path": str(c.GetPath()), "type": c.GetTypeName()} for c in world.GetChildren()
        ]
print(json.dumps(meta, indent=2))
