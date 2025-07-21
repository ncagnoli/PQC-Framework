#!/usr/bin/python3
#
# CLIENT MONITOR
#       by Nestor Cagnoli

import subprocess
import csv
import sys
import signal
import os
import datetime
import socket
import time

# ---------------- SETTINGS ---------------- #
# --- General ---
DEBUG_MODE = True  # Set to True to see detailed commands and outputs
ITERATIONS = 100  # Maximum number of successful test iterations
RESULTS_DIR = "Results"  # Directory where results will be stored
SIGNAL_FILE = "/tmp/stop_server_perf" # File used to signal the server

# --- Client Command Configuration ---
# This command is what 'perf' will measure.
# It should be a command that interacts with the server.

# Example for SSH:
CLIENT_COMMAND = "ssh"
CLIENT_ARGS = [
    "-p", "22", "-i", "id_rsa", "-o", "BatchMode=yes", "-o", "ForwardX11=no",
    "-o", "KexAlgorithms=mlkem768x25519-sha256", "test1@localhost", "echo 'Connection successful'"
]
# For logging purposes, can be a friendly name for the test
TEST_NAME = "mlkem768x25519-sha256"

# --- Server Signaling Configuration ---
# SSH settings used to create/remove the signal file on the server.
# This part is necessarily SSH-specific.
SIGNAL_SSH_USER = "test1"
SIGNAL_SSH_HOST = "localhost"
SIGNAL_SSH_PORT = 22
SIGNAL_SSH_KEY = "id_rsa"
# ------------------------------------------ #

def debug(msg):
    """Prints a debug message if DEBUG_MODE is True."""
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def setup_results_dir():
    """Ensures the results directory exists."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_output_filename():
    """Generates a unique filename for the output CSV."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    hostname = socket.gethostname()
    return os.path.join(RESULTS_DIR, f"{hostname}-{timestamp}-client-{TEST_NAME}.csv")

def execute_perf_on_client(command):
    """Executes a command under 'perf stat' and returns the output and return code."""
    debug(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True, timeout=10)
        debug(f"Perf stderr output:\n{result.stderr}")
        return result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        debug("Command timed out.")
        return "Timeout", -1

def parse_perf_output(output):
    """Parses the stderr output from 'perf stat' to extract metrics."""
    metrics = {
        "cycles": 0, "instructions": 0, "cache-misses": 0,
        "branch-misses": 0, "page-faults": 0, "context-switches": 0, "cpu-migrations": 0
    }
    for line in output.split('\n'):
        parts = line.strip().split()
        if len(parts) > 1:
            value_str = parts[0].replace(',', '').replace('.', '')
            key = parts[1]
            if key in metrics:
                try:
                    metrics[key] = int(value_str)
                except ValueError:
                    metrics[key] = 0
    return metrics

def cleanup_and_exit(signum, frame):
    """Handles script interruption (e.g., CTRL+C) for a clean exit."""
    print("\n[INFO] Interruption detected! Exiting script safely...")
    sys.exit(0)

def signal_server(action):
    """Creates or removes the signal file on the server via SSH."""
    if action not in ["create", "remove"]:
        raise ValueError("Action must be 'create' or 'remove'")

    command_str = f"touch {SIGNAL_FILE}" if action == "create" else f"rm -f {SIGNAL_FILE}"

    ssh_command = [
        "ssh", "-p", str(SIGNAL_SSH_PORT), "-i", SIGNAL_SSH_KEY,
        "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
        f"{SIGNAL_SSH_USER}@{SIGNAL_SSH_HOST}", command_str
    ]

    debug(f"Signaling server ('{action}'): {' '.join(ssh_command)}")
    try:
        result = subprocess.run(ssh_command, timeout=10, check=True, capture_output=True, text=True)
        debug(f"Signaling successful. Server output: {result.stdout}")
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"Error signaling server ('{action}'): {e}", file=sys.stderr)
        if hasattr(e, 'stderr'):
            print(f"Server stderr: {e.stderr}", file=sys.stderr)
        return False

def run_client_benchmark():
    """Main function to run the client-side performance benchmark."""
    setup_results_dir()
    output_file = generate_output_filename()

    perf_command_base = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    client_connection_command = [CLIENT_COMMAND] + CLIENT_ARGS
    full_perf_command = perf_command_base + ["--"] + client_connection_command

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
            "page-faults", "context-switches", "cpu-migrations"
        ])
        
        for i in range(ITERATIONS):
            print(f"\n--- Starting Iteration {i} ---")

            # 1. Ensure the server is ready for a new connection
            print("Preparing server for measurement...")
            if not signal_server("remove"):
                print("Failed to prepare server (removing old signal). Aborting.", file=sys.stderr)
                break

            # Pause to give the server's loop script time to restart server_perf.py
            print("Waiting for server to come online...")
            time.sleep(3)

            # 2. Measure the performance of the client's SSH connection
            print("Running perf on the client...")
            perf_output, return_code = execute_perf_on_client(full_perf_command)

            if return_code != 0:
                print(f"Client measurement failed (return code: {return_code}). Retrying...")
                # If the connection failed, the server might not have started. Give it more time.
                time.sleep(2)
                continue

            print("Client measurement successful!")
            metrics = parse_perf_output(perf_output)
            metrics["iteration"] = i
            writer.writerow([
                metrics["iteration"], metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
            ])

            # 3. Signal the server to stop and record its data
            print("Signaling server to stop and log data...")
            if not signal_server("create"):
                print("Failed to signal server to stop. Aborting test.", file=sys.stderr)
                break

            print(f"--- Finished Iteration {i} ---")

if __name__ == "__main__":
    # Set up signal handlers for graceful exit
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    print(f"Starting client tests. Results will be saved to: {generate_output_filename()}")
    run_client_benchmark()
