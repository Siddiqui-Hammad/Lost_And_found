#o* Smart Lost and Found System - 1-zprefix Launcher
import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")
    print('\n[*] Web Application opened at http://127.0.0.1:8000')

if __name__ == "__main__":
    print("")
    print("=" * 60)
    print(" AI + IoT SMART LOST & FOUND SYSTEM (AKTU MINI PROJECT)")
    print(" Tagline: Find what you lost. Return what you found.")
    print("=" * 60)
    print("[*] Starting FastAPI Server on port 8000...")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
