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

Open Settings → Tools & MCP and click Add Custom MCP. A text file named `mcp.json` will open. Paste the text below into it. The word `command` in that text is the name of a line. That line holds the path to `python.exe`, which sits inside the downloaded folder, in `.venv\Scripts`. The word `args` is the name of the next line. That line holds the path to `server.py` in the same folder. Write each backslash twice. That is how this file is formatted:

```json
{
  "mcpServers": {
    "isaac-scene": {
      "command": "C:\\Users\\NAME\\Desktop\\isaac-scene-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\NAME\\Desktop\\isaac-scene-mcp\\server.py"
      ]
    }
  }
}
```

Replace `NAME` with your Windows user folder name. If you did not put the bridge folder on the desktop, correct the path in both lines, `command` and `args`. If `mcp.json` already contains something, add the `isaac-scene` block inside `mcpServers`, with a comma, and leave the existing lines in place. Save the file. Press Ctrl+Shift+P, type Developer: Reload Window, and run that command. Cursor will reload. Open Settings → Tools & MCP again and turn on the `isaac-scene` switch. A green dot should appear next to the name. A red dot means the path in the `command` line or the `args` line is wrong, or the commands in step 2 have not been run yet.

## 4. Check

In the Cursor chat, ask the agent to look at the open scene. When the connection works, the agent names the objects that are in it.
