# NyayaSim × Ren'Py Integration Guide

This guide explains how to connect a **Ren'Py 8** Visual Novel frontend to the **NyayaSim Python multi-agent backend**.

---

## 1. Architecture Overview

```
┌─────────────────────────────────┐           HTTP POST /api/simulate/batch          ┌──────────────────────────────────┐
│      Ren'Py Visual Novel        │ ───────────────────────────────────────────────> │     NyayaSim FastAPI Server      │
│  - Character Sprites & Dialogue │ <─────────────────────────────────────────────── │  (http://127.0.0.1:8000)         │
│  - Story Choice Menus           │          Returns Full Structured JSON:           │  - BM25 Corpus Statutory Search   │
│  - Click-to-Advance Reader      │          - Sequential Dialogues & Poses          │  - 2-Tier Citation Verifier       │
│  - Python 3 `urllib.request`    │          - Procedural Checklists                 │  - Multi-Agent Court Debate       │
└─────────────────────────────────┘          - Multi-Judge Verdict                   │  - SQLite Audit Logging          │
                                                                                     └──────────────────────────────────┘
```

1. **Backend Server (`backend/server.py`)**: Runs locally using Uvicorn. It exposes:
   - `POST /api/simulate` (Server-Sent Events streaming for web browsers)
   - `POST /api/simulate/batch` (Synchronous JSON array tailored for Ren'Py and game engines)
2. **Ren'Py Engine**: Inside `script.rpy`, Python's standard `urllib.request` sends the chosen dispute case text to `http://127.0.0.1:8000/api/simulate/batch`.
3. **Dialogue Playback**: Ren'Py iterates through the received `dialogues` list, dynamically showing character poses and advancing with every player click/Space press.

---

## 2. Quick Setup Steps

### Step 1: Copy Assets to Ren'Py
In your Ren'Py project folder (`<RenPyProject>/game/`):
1. Copy `renpy/game/script.rpy` into `<RenPyProject>/game/script.rpy`.
2. Copy the background and sprites from `frontend/public/assets/`:
   - `frontend/public/assets/backgrounds/Background.jpg` ➔ `<RenPyProject>/game/images/Background.jpg`
   - `frontend/public/assets/sprites/` ➔ `<RenPyProject>/game/images/sprites/`

### Step 2: Start the NyayaSim Backend
Open a terminal in the NyayaSim project root:
```bash
py -3.11 -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
```
Or double-click `start_renpy_sim.bat`.

### Step 3: Launch Ren'Py
Open the **Ren'Py Launcher**, choose your project, and click **Launch Project**.
When you click **Start**, Ren'Py will:
- Present a case selection menu.
- Query the backend API.
- Play out the courtroom trial line-by-line with character portraits and poses!
