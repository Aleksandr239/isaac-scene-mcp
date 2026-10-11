import json
import os

_MCP_SCRIPTS_DIR = r"__SCRIPTS_DIR__"
_MCP_FN = """__FN__"""
_MCP_ARGS_JSON = r"""__ARGS_JSON__"""

_mcp_harness_path = os.path.join(_MCP_SCRIPTS_DIR, "mcp_harness.py")
_mcp_mtime = os.path.getmtime(_mcp_harness_path)
if globals().get("_MCP_HARNESS_MTIME") != _mcp_mtime:
    exec(open(_mcp_harness_path, encoding="utf-8").read(), globals())
    globals()["_MCP_HARNESS_MTIME"] = _mcp_mtime

if _MCP_FN not in globals():
    raise RuntimeError(f"harness function missing: {_MCP_FN}")

_mcp_args = json.loads(_MCP_ARGS_JSON) if _MCP_ARGS_JSON.strip() not in ("", "{}") else {}
print(json.dumps(globals()[_MCP_FN](**_mcp_args), indent=2, ensure_ascii=False, default=str))
