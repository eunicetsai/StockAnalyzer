"""
Entry point for running the Stock Analyzer application.

Usage:
    python -m stock_analyzer
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit application."""
    # Get the directory containing this file
    module_dir = Path(__file__).parent
    app_path = module_dir / "app.py"
    
    # Launch Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


if __name__ == "__main__":
    main()
