"""Isaac Scene MCP — Cursor bridge to a live Isaac Sim stage via TCP :8226."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mcp.server.fastmcp import FastMCP

from isaac_client import IsaacPythonServerError, run_and_format
from queries import load

mcp = FastMCP("isaac-scene")

_SCRIPTS = _ROOT / "scripts"
_LOGS = _ROOT / "logs"
_CONTROLLERS = _ROOT / "controllers.json"
_EPISODE_LOG = _LOGS / "episodes.jsonl"

_PRESETS = {
    "table_approach": "H1 3 m north of the table, facing the drill",
    "table_near": "H1 at stand-off for arm tests (skip the 3 m walk)",
}


def _run(source: str, timeout: float = 60.0) -> str:
    try:
        return run_and_format(source, timeout=timeout)
    except IsaacPythonServerError as exc:
        return "ERROR: " + str(exc)


def _parse_json_blob(text: str) -> dict:
    raw = (text or "").strip()
    if raw.startswith("ERROR:"):
        raise IsaacPythonServerError(raw)
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start = raw.rfind("\n{")
    chunk = raw[start + 1 :] if start >= 0 else raw[raw.find("{") :]
    data = json.loads(chunk)
    if not isinstance(data, dict):
        raise IsaacPythonServerError("Isaac harness did not return a JSON object")
    return data


def _harness(fn: str, timeout: float = 90.0, **kwargs) -> str:
    return _run(
        load(
            "harness_call",
            scripts_dir=str(_SCRIPTS).replace("\\", "/"),
            fn=fn,
            args_json=json.dumps(kwargs, ensure_ascii=False),
        ),
        timeout=timeout,
    )


def _harness_json(fn: str, timeout: float = 90.0, **kwargs) -> dict:
    return _parse_json_blob(_harness(fn, timeout=timeout, **kwargs))


def _append_episode(record: dict) -> None:
    _LOGS.mkdir(parents=True, exist_ok=True)
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with _EPISODE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _run_episode_internal(
    controller: str,
    seconds: float,
    reset: bool,
    preset: str,
    poll_seconds: float,
) -> dict:
    started = time.time()
    if reset:
        reset_info = _harness_json("mcp_reset_to_golden", preset=preset)
        if not reset_info.get("ok", True):
            return {"ok": False, "step": "reset", "reset": reset_info}
    else:
        reset_info = {"skipped": True}

    load_info = None
    if controller and controller != "none":
        load_info = _harness_json("mcp_load_controller", timeout=120.0, name=controller)
        if not load_info.get("ok", True):
            return {"ok": False, "step": "load_controller", "reset": reset_info, "load": load_info}

    samples: list[dict] = []
    last: dict = {}
    deadline = time.time() + max(1.0, float(seconds))
    while True:
        last = _harness_json("mcp_get_live_state", timeout=30.0)
        samples.append(
            {
                "t": round(time.time() - started, 2),
                "phase": last.get("phase"),
                "pelvis": last.get("pelvis"),
                "hand_drill_dist": last.get("hand_drill_dist"),
                "fallen": last.get("fallen"),
                "grasped": last.get("grasped"),
            }
        )
        if last.get("terminal"):
            break
        if time.time() >= deadline:
            last["terminal"] = True
            last["terminal_reason"] = last.get("terminal_reason") or "timeout"
            break
        time.sleep(max(0.2, float(poll_seconds)))

    record = {
        "ok": True,
        "controller": controller,
        "preset": preset,
        "seconds_requested": seconds,
        "elapsed_s": round(time.time() - started, 2),
        "reset": reset_info,
        "load": load_info,
        "final": last,
        "samples": samples[-24:],
        "metrics": {
            "fallen": bool(last.get("fallen")),
            "grasped": bool(last.get("grasped")),
            "phase": last.get("phase"),
            "hand_drill_dist": last.get("hand_drill_dist"),
            "walked_m": last.get("walked_m"),
            "pelvis": last.get("pelvis"),
            "terminal_reason": last.get("terminal_reason"),
        },
    }
    _append_episode(
        {
            "controller": controller,
            "preset": preset,
            "elapsed_s": record["elapsed_s"],
            "metrics": record["metrics"],
        }
    )
    return record


@mcp.tool()
def ping() -> str:
    """Check that Isaac Sim python_server is reachable on 127.0.0.1:8226."""
    return _run(load("ping"), timeout=15.0)


@mcp.tool()
def get_scene_meta() -> str:
    """Return stage units, up-axis, default prim, play state, and /World children."""
    return _run(load("scene_meta"))


@mcp.tool()
def list_prims(
    prefix: str = "/World",
    max_depth: int = 8,
    limit: int = 400,
) -> str:
    """List prims under a path prefix (path, type, depth)."""
    return _run(
        load(
            "list_prims",
            prefix=prefix,
            max_depth=str(max_depth),
            limit=str(limit),
        ),
        timeout=90.0,
    )


@mcp.tool()
def get_prim_info(prim_path: str) -> str:
    """Inspect one prim: type, children, transform, collision, world bbox."""
    return _run(load("get_prim_info", prim_path=prim_path))


@mcp.tool()
def get_robot_snapshot(robot_path: str = "/World/nova_carter") -> str:
    """Snapshot robot pose, bbox, drive joints, and live joint state if available."""
    return _run(load("robot_snapshot", robot_path=robot_path), timeout=90.0)


@mcp.tool()
def get_mesh_bboxes(
    prefix: str = "/World",
    min_size: float = 0.5,
    limit: int = 200,
) -> str:
    """List large mesh world AABBs (floors/walls) for navigation planning."""
    return _run(
        load(
            "mesh_bboxes",
            prefix=prefix,
            min_size=str(min_size),
            limit=str(limit),
        ),
        timeout=120.0,
    )


@mcp.tool()
def execute_python(code: str, timeout_seconds: float = 60.0) -> str:
    """Execute arbitrary Python inside the running Isaac Sim session.

    Use for controllers, scene edits, and debugging. State persists across calls
    in the same Isaac session. Prefer specialized tools for reads when possible.
    """
    return _run(code, timeout=timeout_seconds)


@mcp.tool()
def timeline(action: str = "status") -> str:
    """Control simulation timeline: play | pause | stop | status.

    Prefer pause over stop. Stop has crashed this Isaac session before.
    For tests use reset_to_golden instead of stop.
    """
    action = action.strip().lower()
    if action not in ("play", "pause", "stop", "status"):
        return "ERROR: action must be one of: play, pause, stop, status"
    if action == "stop":
        return (
            "ERROR: timeline stop is disabled in this MCP. "
            "Use reset_to_golden (pause + poses) or timeline pause. "
            "Isaac Stop has dropped the python_server connection."
        )
    return _run(load("timeline", action=action))


@mcp.tool()
def list_bench() -> str:
    """List golden presets and named controllers. Does not need Isaac."""
    controllers = {}
    if _CONTROLLERS.is_file():
        controllers = json.loads(_CONTROLLERS.read_text(encoding="utf-8"))
    return json.dumps(
        {
            "presets": _PRESETS,
            "controllers": {
                name: (spec or {}).get("description", "") for name, spec in controllers.items()
            },
            "episode_log": str(_EPISODE_LOG),
        },
        indent=2,
        ensure_ascii=False,
    )


@mcp.tool()
def reset_to_golden(preset: str = "table_approach") -> str:
    """Reset H1 and the drill to a known pose without Stop.

    Presets: table_approach (3 m north of table), table_near (arm tests).
    Pauses timeline, sets translate+rotateZ, removes the grasp joint.
    """
    return _harness("mcp_reset_to_golden", preset=preset)


@mcp.tool()
def get_live_state() -> str:
    """One-shot metrics: pelvis, hand, drill, distance, phase, fallen, grasped."""
    return _harness("mcp_get_live_state", timeout=30.0)


@mcp.tool()
def load_controller(name: str = "grasp") -> str:
    """Load a named controller script into Isaac and start it.

    Names: grasp, walk, none, mount_cinematic. See list_bench.
    """
    return _harness("mcp_load_controller", timeout=120.0, name=name)


@mcp.tool()
def stop_controller() -> str:
    """Stop walk/grasp loops without stopping the Isaac timeline."""
    return _harness("mcp_stop_loops")


@mcp.tool()
def set_task(hanger_id: str = "425261") -> str:
    """Set the BIM target (Revit id, e.g. 425261 hanger). Stores world XYZ for later skills."""
    return _harness("mcp_set_task", hanger_id=hanger_id)


@mcp.tool()
def run_episode(
    controller: str = "grasp",
    seconds: float = 25.0,
    reset: bool = True,
    preset: str = "table_approach",
    poll_seconds: float = 0.5,
) -> str:
    """Run one test: optional reset, start controller, poll until success/fail/timeout.

    Returns metrics JSON (fallen, grasped, hand_drill_dist, phase). Appends logs/episodes.jsonl.
    Does not Stop Isaac. Physics keeps running while this tool polls.
    """
    try:
        record = _run_episode_internal(controller, seconds, reset, preset, poll_seconds)
    except IsaacPythonServerError as exc:
        return "ERROR: " + str(exc)
    return json.dumps(record, indent=2, ensure_ascii=False, default=str)


@mcp.tool()
def run_batch(
    n: int = 3,
    controller: str = "grasp",
    seconds: float = 20.0,
    preset: str = "table_approach",
    poll_seconds: float = 0.5,
) -> str:
    """Run n sequential episodes on the live Isaac GUI. Sequential, not parallel.

    Each episode resets to the golden preset. Returns per-run metrics plus counts.
    """
    n = max(1, min(int(n), 20))
    runs = []
    try:
        for i in range(n):
            rec = _run_episode_internal(controller, seconds, True, preset, poll_seconds)
            runs.append(
                {
                    "i": i + 1,
                    "ok": rec.get("ok"),
                    "metrics": rec.get("metrics") or rec,
                    "elapsed_s": rec.get("elapsed_s"),
                }
            )
    except IsaacPythonServerError as exc:
        return "ERROR: " + str(exc)
    fallen = sum(1 for r in runs if (r.get("metrics") or {}).get("fallen"))
    grasped = sum(1 for r in runs if (r.get("metrics") or {}).get("grasped"))
    summary = {
        "n": n,
        "controller": controller,
        "preset": preset,
        "fallen": fallen,
        "grasped": grasped,
        "runs": runs,
    }
    _append_episode({"batch_summary": True, **{k: summary[k] for k in ("n", "controller", "preset", "fallen", "grasped")}})
    return json.dumps(summary, indent=2, ensure_ascii=False, default=str)


@mcp.tool()
def get_episode_logs(limit: int = 10) -> str:
    """Read the last N episode records from logs/episodes.jsonl."""
    limit = max(1, min(int(limit), 100))
    if not _EPISODE_LOG.is_file():
        return json.dumps({"records": [], "path": str(_EPISODE_LOG)})
    lines = _EPISODE_LOG.read_text(encoding="utf-8").splitlines()
    recs = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            recs.append({"raw": line})
    return json.dumps({"path": str(_EPISODE_LOG), "records": recs}, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
