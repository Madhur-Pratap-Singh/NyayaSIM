"""
NyayaSim GBA Courtroom Launcher
Launches both the FastAPI SSE backend (port 8000) and the Vite React frontend (port 5173).
"""

import subprocess
import sys
import time
import os
import webbrowser

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 65)
    print("  NYAYASIM: GBA-STYLE COURTROOM SIMULATOR")
    print("  Indian Consumer Disputes Redressal Commission (CPA 2019)")
    print("=" * 65)

    # 1. Start FastAPI Backend
    print("\n[1/2] Starting FastAPI Backend on http://localhost:8000 ...")
    backend_cmd = [
        "py", "-3.11", "-m", "uvicorn", "backend.server:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=WORKSPACE_ROOT)
    time.sleep(2)

    # 2. Start Vite Frontend
    print("[2/2] Starting Vite React Frontend on http://localhost:5173 ...")
    frontend_dir = os.path.join(WORKSPACE_ROOT, "frontend")
    frontend_cmd = ["npm.cmd", "run", "dev"] if os.name == "nt" else ["npm", "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir)
    time.sleep(3)

    print("\n" + "=" * 65)
    print("  -> FRONTEND: http://localhost:5173")
    print("  -> BACKEND:  http://localhost:8000/docs")
    print("=" * 65)
    print("\nPress Ctrl+C to terminate both servers.\n")

    try:
        webbrowser.open("http://localhost:5173")
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
