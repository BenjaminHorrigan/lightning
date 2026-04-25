#!/usr/bin/env python3
"""
Simple script to run the Lightning FastAPI demo.
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run the Lightning FastAPI demo server."""
    demo_path = Path(__file__).parent / "demos" / "fastapi_app.py"

    if not demo_path.exists():
        print(f"Error: Demo file not found at {demo_path}")
        sys.exit(1)

    print("🚀 Starting Lightning FastAPI Demo Server...")
    print("🌐 Open your browser to: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("⚡ Press Ctrl+C to stop")
    print()

    try:
        subprocess.run([sys.executable, str(demo_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()