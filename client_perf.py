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
import config
import parsing_util

def debug(msg):
    """Prints a debug message if DEBUG_MODE is True."""
    if config.DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def setup_results_dir():
    """Ensures the results directory exists."""
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

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

def cleanup_and_exit(signum, frame):
    """Handles script interruption (e.g., CTRL+C) for a clean exit."""
    print("\n[INFO] Interruption detected! Exiting script safely...")
    sys.exit(0)

def signal_server(action):
    """Creates or removes the signal file on the server via SSH."""
    if action not in ["create", "remove"]:
        raise ValueError("Action must be 'create' or 'remove'")

    command_str = f"touch {config.SIGNAL_FILE}" if action == "create" else f"rm -f {config.SIGNAL_FILE}"

    ssh_command = [
        "ssh", "-p", str(config.SIGNAL_SSH_PORT), "-i", config.SIGNAL_SSH_KEY,
        "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
        f"{config.SIGNAL_SSH_USER}@{config.SIGNAL_SSH_HOST}", command_str
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

def run_client_benchmark(output_filename):
    """
    Main function to run the client-side performance benchmark.

    Args:
        output_filename (str): The path to the CSV file for logging results.
    """
    setup_results_dir()

    # Write header only if the file doesn't exist
    if not os.path.exists(output_filename):
        with open(output_filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(parsing_util.CSV_HEADERS)

    perf_command_base = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    client_connection_command = [config.CLIENT_COMMAND] + config.CLIENT_ARGS
    full_perf_command = perf_command_base + ["--"] + client_connection_command

    for i in range(config.ITERATIONS):
        print(f"\n--- Starting Iteration {i} ---")

        # A short pause to allow the server to restart from the previous iteration.
        time.sleep(2)

        print("Running perf on the client to connect and signal the server...")
        perf_output, return_code = execute_perf_on_client(full_perf_command)

        if "Timeout" in perf_output:
             print(f"Client measurement timed out. Retrying...")
             continue

        print("Client measurement captured!")
        metrics = parsing_util.parse_perf_output(perf_output, i)
        
        with open(output_filename, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=parsing_util.CSV_HEADERS)
            writer.writerow(metrics)

        print(f"--- Finished Iteration {i} ---")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./client_perf.py <output_filename>", file=sys.stderr)
        sys.exit(1)

    output_file = sys.argv[1]

    # Set up signal handlers for graceful exit
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    print(f"Starting client tests. Results will be saved to: {output_file}")
    run_client_benchmark(output_file)
