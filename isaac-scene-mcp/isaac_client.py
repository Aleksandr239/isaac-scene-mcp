"""TCP client for Isaac Sim isaacsim.code_editor.python_server (default 127.0.0.1:8226)."""

import json
import os
import socket
from typing import Any

DEFAULT_HOST = os.environ.get("ISAAC_PYTHON_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("ISAAC_PYTHON_SERVER_PORT", "8226"))
DEFAULT_TIMEOUT = float(os.environ.get("ISAAC_PYTHON_SERVER_TIMEOUT", "60"))


class IsaacPythonServerError(RuntimeError):
    """Raised when the Isaac Python server is unreachable or returns an error."""


def execute(
    source: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Send Python source to Isaac Sim and return the JSON response (sync sockets)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(min(10.0, timeout))
    try:
        try:
            sock.connect((host, port))
        except OSError as exc:
            raise IsaacPythonServerError(
                f"Cannot connect to Isaac Python server at {host}:{port}. "
                "Enable Window -> Extensions -> isaacsim.code_editor.python_server "
                "and keep Isaac Sim open with your scene."
            ) from exc

        sock.settimeout(timeout)
        sock.sendall(source.encode("utf-8"))
        # Half-close write side so Isaac knows the request is complete (required).
        try:
            sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        chunks: list[bytes] = []
        while True:
            try:
                chunk = sock.recv(65536)
            except socket.timeout as exc:
                raise IsaacPythonServerError(
                    f"Timed out waiting for Isaac response after {timeout}s."
                ) from exc
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
    finally:
        try:
            sock.close()
        except OSError:
            pass

    if not data:
        raise IsaacPythonServerError("Empty response from Isaac Python server.")

    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise IsaacPythonServerError(
            f"Invalid JSON from Isaac: {data[:500]!r}"
        ) from exc


def format_result(response: dict[str, Any]) -> str:
    """Turn Isaac JSON response into a readable string for MCP tool output."""
    status = response.get("status")
    if status == "ok":
        parts: list[str] = []
        output = response.get("output")
        if output:
            parts.append(str(output).rstrip())
        if "result" in response and response["result"] is not None:
            result = response["result"]
            if isinstance(result, (dict, list)):
                parts.append(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                parts.append(str(result))
        return "\n".join(parts) if parts else "ok"
    ename = response.get("ename", "Error")
    evalue = response.get("evalue", "")
    tb = response.get("traceback") or []
    lines = [f"{ename}: {evalue}"]
    if tb:
        lines.append("\n".join(tb))
    output = response.get("output")
    if output:
        lines.append(str(output))
    return "\n".join(lines)


def run_and_format(
    source: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Execute code in Isaac and return formatted text (raises on connection failure)."""
    response = execute(source, host=host, port=port, timeout=timeout)
    text = format_result(response)
    if response.get("status") != "ok":
        raise IsaacPythonServerError(text)
    return text