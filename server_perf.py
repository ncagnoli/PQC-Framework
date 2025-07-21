#!/usr/bin/python3
#
# SERVER MONITOR
#       by Nestor Cagnoli

import subprocess
import csv
import sys
import os
import datetime
import socket
import time
import signal

# ---------------- SETTINGS ---------------- #
# --- General ---
DEBUG_MODE = True  # Set to True to see detailed commands and outputs
RESULTS_DIR = "Results"  # Directory where results will be stored
SIGNAL_FILE = "/tmp/stop_server_perf" # File used to signal the server to stop

# --- Server Command Configuration ---
# Example for SSHD:
SERVER_BINARY = "/usr/sbin/sshd"
SERVER_ARGS = ["-D", "-e", "-p", "22", "-f", "./sshd_config_mlkem768x25519-sha256"]
# The script will try to find the config file path from the arguments (looks for '-f').
# If not found, the output filename will be 'generic'.
PORT_TO_CHECK = 22 # Port to check for availability, 'None' to disable.
# ------------------------------------------ #

def debug(msg):
    """Prints a debug message if DEBUG_MODE is True."""
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def is_port_in_use(port):
    """Checks if a given TCP port is already in use."""
    if port is None:
        return False
    command = ["ss", "-tln"]
    debug(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    return f":{port} " in result.stdout

def setup_results_dir():
    """Ensures the results directory exists."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

def get_config_from_args(args):
    """Finds a config file path in the server arguments, typically after a '-f' flag."""
    try:
        # Find the index of the flag (e.g., '-f')
        idx = args.index('-f')
        # The config file path should be the next item
        if idx + 1 < len(args):
            return args[idx + 1]
    except ValueError:
        # The flag was not found
        pass
    return None

def generate_output_filename():
    """Generates a unique filename for the output CSV based on timestamp, hostname, and config."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    config_path = get_config_from_args(SERVER_ARGS)
    config_filename = os.path.basename(config_path) if config_path else "generic"

    hostname = socket.gethostname()
    return os.path.join(RESULTS_DIR, f"{hostname}-{timestamp}-server-{config_filename}.csv")

def parse_perf_output(output):
    """Parses the stderr output from 'perf stat' to extract metrics."""
    metrics = {
        "cycles": 0, "instructions": 0, "cache-misses": 0,
        "branch-misses": 0, "page-faults": 0, "context-switches": 0, "cpu-migrations": 0
    }
    for line in output.split('\n'):
        # Look for lines containing a number and a metric
        parts = line.strip().split()
        if len(parts) > 1:
            value_str = parts[0].replace(',', '').replace('.', '')
            key = parts[1]
            if key in metrics:
                try:
                    metrics[key] = int(value_str)
                except ValueError:
                    metrics[key] = 0 # Ignore if not a number
    return metrics

def run_server_benchmark():
    """Main function to run the target server binary under 'perf stat' and wait for a signal."""
    if is_port_in_use(PORT_TO_CHECK):
        print(f"Error: Port {PORT_TO_CHECK} is already in use.", file=sys.stderr)
        sys.exit(1)

    setup_results_dir()

    # Ensure no old signal file is present
    if os.path.exists(SIGNAL_FILE):
        os.remove(SIGNAL_FILE)

    perf_command = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    server_command = [SERVER_BINARY] + SERVER_ARGS
    full_command = perf_command + ["--"] + server_command

    try:
        print(f"Starting server binary '{SERVER_BINARY}' with perf...")
        debug(f"Running command: {' '.join(full_command)}")

        server_process = subprocess.Popen(full_command, stderr=subprocess.PIPE, text=True)
        debug(f"'perf {os.path.basename(SERVER_BINARY)}' server started with PID: {server_process.pid}")

        # Loop to wait for the signal file
        while not os.path.exists(SIGNAL_FILE):
            time.sleep(1)
            # Check if the process terminated unexpectedly
            if server_process.poll() is not None:
                print("Error: The server process terminated unexpectedly.", file=sys.stderr)
                stderr = server_process.stderr.read()
                debug(f"Server stderr output:\n{stderr}")
                break

        print("\n[INFO] Signal received to stop the server.")

        # Send SIGINT to the perf process, which should forward it to the server binary
        server_process.send_signal(signal.SIGINT)

        # Wait for the process to terminate and capture its output
        server_process.wait(timeout=10)
        stderr_output = server_process.stderr.read()
        debug(f"Final perf stderr output:\n{stderr_output}")

        # Parse the perf output and save to CSV
        output_file = generate_output_filename()
        with open(output_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "cycles", "instructions", "cache-misses", "branch-misses",
                "page-faults", "context-switches", "cpu-migrations"
            ])
            metrics = parse_perf_output(stderr_output)
            writer.writerow([
                metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
            ])
        print(f"Server results saved to: {output_file}")

    except subprocess.TimeoutExpired:
        print("Timeout waiting for the server to terminate. Forcefully killing.", file=sys.stderr)
        server_process.kill()
    except KeyboardInterrupt:
        print("\n[INFO] CTRL+C detected! Shutting down the server safely...")
        if 'server_process' in locals() and server_process.poll() is None:
            server_process.send_signal(signal.SIGINT)
            server_process.wait()
    finally:
        # Clean up the signal file on exit
        if os.path.exists(SIGNAL_FILE):
            os.remove(SIGNAL_FILE)
        print("Server has shut down.")

if __name__ == "__main__":
    run_server_benchmark()