import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCENARIO = 'health_gathering_supreme'

def main():
    cmd = [sys.executable, str(ROOT / 'scenario_pipeline.py'), '--scenario', SCENARIO, '--stage', 'all', *sys.argv[1:]]
    raise SystemExit(subprocess.run(cmd, check=False).returncode)

if __name__ == '__main__':
    main()
