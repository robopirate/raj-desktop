"""main.py — legacy entry point. The legacy customtkinter UI was removed.
Use this shim, or run desktop.py / START.bat directly."""
import runpy
import os

if __name__ == "__main__":
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop.py"), run_name="__main__")
