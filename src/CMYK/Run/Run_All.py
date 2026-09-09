import subprocess
import sys
from ftplib import print_line
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent


def run_sequential_scripts():
    scripts = [
        RUN_DIR / "Turbofan_001.py",
        RUN_DIR / "Turbofan_002.py",
        RUN_DIR / "Turbofan_003.py"
    ]

    for script in scripts:
        print(f"--> Running {script.name} ... ", end="")

        try:
            subprocess.run([sys.executable, str(script)], check=True)
            print(f"Finished successfully :D")
        except subprocess.CalledProcessError:
            continue

if __name__ == "__main__":
    run_sequential_scripts()