import argparse
import signal
import sys
import time
import os
import json
from json import JSONDecodeError
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError
from simulator import Simulator
from utils.exceptions.simulator_validation_error import SimulatorValidationError
from utils.print_validation_error import print_validation_error
from utils.read_publishers import read_publishers

def default_settings() -> Path:
    base_folder = Path(__file__).resolve().parent.parent
    settings_file = base_folder / "config/settings.json"
    return settings_file

def is_valid_file(arg: str) -> Path:
    settings_file = Path(arg)
    if not settings_file.is_file():
        raise argparse.ArgumentTypeError(f"argument -f/--file: can't open '{arg}'")
    return settings_file

# ==========================================
# 1. KUBERNETES CONFIG LOADER
# ==========================================
# Checks if K8s injected config via Env Var. 
# If so, writes it to the default file location.
env_config = os.getenv("SIMULATOR_CONFIG_JSON")
if env_config:
    try:
        print("[INIT] Found SIMULATOR_CONFIG_JSON environment variable.")
        # Parse to ensure it's valid JSON
        config_data = json.loads(env_config)
        
        # Define target path (Standard location)
        target_path = default_settings()
        
        # Ensure folder exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(target_path, "w") as f:
            json.dump(config_data, f, indent=2)
            
        print(f"[INIT] Successfully wrote config to {target_path}")
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse SIMULATOR_CONFIG_JSON: {e}")
        # We don't exit here; we let the file argument handler try its luck
    except Exception as e:
        print(f"[ERROR] Failed to write config file: {e}")

# ==========================================
# 2. STANDARD ARGUMENT PARSING
# ==========================================

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--file",
    dest="settings_file",
    type=is_valid_file,
    help="settings file path",
    default=default_settings(),
    metavar="",
)
parser.add_argument(
    "-v",
    "--verbose",
    dest="is_verbose",
    action="store_true",
    help="enable verbose output",
    default=False
)
args = parser.parse_args()

try:
    publishers = read_publishers(args.settings_file, args.is_verbose)
except (JSONDecodeError, PydanticValidationError, SimulatorValidationError) as e:
    print_validation_error(e)
    sys.exit(1)

simulator = Simulator(publishers)

# Set up signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\n\nShutting down gracefully...")
    simulator.stop()
    # Give threads time to clean up
    time.sleep(2)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Start the simulator
simulator.run()

# Keep the main thread alive while publishers are running
try:
    while any(p.is_alive() for p in simulator.publishers):
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nShutting down gracefully...")
    simulator.stop()
    time.sleep(2)