#!/usr/bin/python3

import subprocess
import csv
import sys
import signal
import os
import datetime
import socket
import time
import config

def debug(msg):
    """Prints a debug message if DEBUG_MODE is True."""
    if config.DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def setup_results_dir():
    """Ensures the results directory exists."""
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

def generate_output_filename():
    """Generates a unique filename for the output CSV."""
    # Nome de arquivo só com data (YYYYMMDD), hostname e TEST_NAME, para facilitar append
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    hostname = socket.gethostname()
    return os.path.join(config.RESULTS_DIR, f"{hostname}-{timestamp}-client-{config.TEST_NAME}.csv")

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

def run_client_benchmark():
    """Main function to run the client-side performance benchmark."""
    setup_results_dir()
    output_file = generate_output_filename()

    perf_command_base = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    client_connection_command = [config.CLIENT_COMMAND] + config.CLIENT_ARGS
    full_perf_command = perf_command_base + ["--"] + client_connection_command

    file_exists = os.path.isfile(output_file)
    with open(output_file, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "iteration", "timestamp", "cycles", "instructions", "cache-misses", "branch-misses",
                "page-faults", "context-switches", "cpu-migrations"
            ])
        
        for i in range(config.ITERATIONS):
            print(f"\n--- Starting Iteration {i} ---")

            # Pausa para garantir o servidor pronto entre iterações
            time.sleep(2)

            print("Running perf on the client to connect and signal the server...")
            perf_output, return_code = execute_perf_on_client(full_perf_command)

            if "Timeout" in perf_output:
                print(f"Client measurement timed out. Retrying...")
                continue

            print("Client measurement captured!")
            metrics = parse_perf_output(perf_output)
            metrics["iteration"] = i
            writer.writerow([
                metrics["iteration"], datetime.datetime.now().isoformat(), metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
            ])

            print(f"--- Finished Iteration {i} ---")

    print(f"\n[INFO] Todos os resultados foram adicionados em: {output_file}")

if __name__ == "__main__":
    # Set up signal handlers for graceful exit
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    print(f"Starting client tests. Results will be appended to: {generate_output_filename()}")
    run_client_benchmark()
