import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCENARIO = 'learning'

def main():
    cmd = [sys.executable, str(ROOT / 'scenario_play.py'), '--scenario', SCENARIO, *sys.argv[1:]]
    raise SystemExit(subprocess.run(cmd, check=False).returncode)

if __name__ == '__main__':
    main()
