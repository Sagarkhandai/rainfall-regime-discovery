import sys
import os
import time
import webbrowser
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

def check_libraries():
    print("=" * 70)
    print("   RAINFALL ATLAS - 3D CLIMATE INTELLIGENCE PLATFORM")
    print("=" * 70)
    print("\n[1/3] Verifying Python Libraries...")

    required_libraries = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("scikit-learn", "sklearn"),
        ("joblib", "joblib"),
        ("python-multipart", "multipart")
    ]

    missing = []
    for display_name, import_name in required_libraries:
        try:
            mod = __import__(import_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"  [OK] {display_name:<18} (version: {ver})")
        except ImportError:
            print(f"  [MISSING] {display_name}")
            missing.append(display_name)

    if missing:
        print(f"\n[!] Missing packages: {', '.join(missing)}")
        print("    Installing missing packages now via pip...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("    [OK] All dependencies successfully installed.")
    else:
        print("\n[2/3] All scientific machine learning libraries are verified!")

def start_server():
    import uvicorn
    from app.main import app

    server_url = "http://127.0.0.1:8000"
    print(f"\n[3/3] Starting Rainfall Atlas Platform on {server_url} ...")
    print("      Warming 145,460 Bureau of Meteorology records...")
    print(f"      Opening browser to {server_url} ...\n")

    # Launch browser only after server is verified ready
    def open_browser():
        import urllib.request
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"{server_url}/api/info", timeout=1) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                time.sleep(1.0)
        time.sleep(0.5)
        print(f"      [READY] Server ready! Opening browser to {server_url} ...\n")
        webbrowser.open(server_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn directly
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    try:
        check_libraries()
        start_server()
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

