#!/usr/bin/env python3
"""
Simple script to run the AEGIS FastAPI demo.
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("🛡️ Starting AEGIS FastAPI Demo Server...")

    # Change to demos directory
    demos_dir = Path(__file__).parent / "demos"

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "fastapi_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=demos_dir, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down AEGIS demo server...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()