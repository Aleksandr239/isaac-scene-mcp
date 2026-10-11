ENG

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

RUS

# Isaac Scene MCP

Локальный мост от Cursor к открытой сцене NVIDIA Isaac Sim.
Cursor запускает `server.py`. Сцена остаётся на вашем компьютере. Isaac Sim слушает `127.0.0.1:8226`.

## Файлы

- `server.py` — файл, который запускает Cursor.
- `isaac_client.py` — передаёт запрос в Isaac Sim и возвращает ответ.
- `queries` — запросы, которыми мост читает сцену.
- `requirements.txt` — библиотека для запуска моста.
- `mcp.example.json` — образец подключения в Cursor. В нём нужно заменить `NAME` на своё имя пользователя и путь на то место, куда вы положили эту папку.

Папку скачивайте целиком. Эти файлы должны лежать рядом, как в репозитории.

## 1. Isaac Sim

Откройте сцену в Isaac Sim. Зайдите в Window → Extensions, найдите `isaacsim.code_editor.python_server` и включите его. Пока Isaac Sim открыт, сервер принимает команды только на этом компьютере, через порт 8226.

## 2. Библиотека моста

Установите Python с python.org, если его ещё нет. При установке включите Add python.exe to PATH.

Откройте эту папку в проводнике, щёлкните по адресной строке, впишите `powershell` и нажмите Enter. Выполните две команды по очереди:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Первая создаёт папку `.venv`. Вторая ставит в неё библиотеку. Дождитесь окончания второй команды без красного текста. Папку `.venv` создаёт каждый у себя, в репозитории её нет.

## 3. Подключение в Cursor

Откройте Settings → Tools & MCP и нажмите Add Custom MCP. Откроется файл `mcp.json`. Добавьте сервер `isaac-scene` по образцу из `mcp.example.json`. В `command` укажите путь к `.venv\Scripts\python.exe` внутри скачанной папки. В `args` укажите путь к `server.py` в той же папке. Каждый обратный слэш в JSON пишите дважды.

Если в `mcp.json` уже есть другие серверы, допишите блок `isaac-scene` внутрь `mcpServers` через запятую и оставьте остальное на месте.

Сохраните файл. Нажмите Ctrl+Shift+P, введите Developer: Reload Window и выполните эту команду. Снова откройте Settings → Tools & MCP и включите переключатель `isaac-scene`. Рядом с именем должна гореть зелёная точка.

## 4. Проверка

В чате Cursor попросите агента посмотреть открытую сцену. Если связь есть, он назовёт объекты, которые в ней стоят.
