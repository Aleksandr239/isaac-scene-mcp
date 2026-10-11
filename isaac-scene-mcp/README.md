# Isaac Scene MCP

Local bridge from Cursor to an open NVIDIA Isaac Sim scene.
Cursor starts `server.py`. The scene stays on your computer. Isaac Sim listens on `127.0.0.1:8226`.

## Files

- `server.py` is the file Cursor starts.
- `isaac_client.py` sends a request to Isaac Sim and returns the answer.
- `queries` holds the scripts that read the scene.
- `requirements.txt` is the library list for the bridge.
- `mcp.example.json` is the Cursor connection sample. Replace `NAME` with your Windows user name and the path with the folder where you saved this project.

Download the folder as a whole. These files have to stay next to each other, as they are in the repository.

## 1. Isaac Sim

Open the scene in Isaac Sim. Go to Window, then Extensions, find `isaacsim.code_editor.python_server`, and enable it. While Isaac Sim is open, the server accepts commands only on this computer, on port 8226.

## 2. Bridge library

Install Python from python.org if you do not have it yet. During setup, turn on Add python.exe to PATH.

Open this folder in File Explorer, click the address bar, type `powershell`, and press Enter. Run these two commands, one after the other:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

The first command creates a `.venv` folder. The second installs the library into it. Wait until the second command finishes with no red text. Each person creates `.venv` locally. It is not in the repository.

## 3. Connect Cursor

Open Settings, then Tools and MCP, and click Add Custom MCP. That opens `mcp.json`. Add an `isaac-scene` server using `mcp.example.json` as the pattern. In `command`, set the path to `.venv\Scripts\python.exe` inside the downloaded folder. In `args`, set the path to `server.py` in the same folder. In JSON, write each backslash twice.

If `mcp.json` already has other servers, add the `isaac-scene` block inside `mcpServers`, separated by a comma, and leave the rest in place.

Save the file. Press Ctrl+Shift+P, type Developer: Reload Window, and run that command. Open Settings, then Tools and MCP again, and turn on `isaac-scene`. The dot next to the name should be green.

## 4. Check

In the Cursor chat, ask the agent to look at the open scene. When the connection works, the agent names the objects that are in it.
