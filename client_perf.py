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
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
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
    metrics = {event: 0 for event in config.PERF_EVENTS}
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

def signal_server():
    """Signals the server to stop by connecting to the signaling port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((config.SIGNAL_SSH_HOST, config.SIGNAL_PORT))
            debug("Signal sent to server.")
            return True
    except ConnectionRefusedError:
        print("Error: Connection to signal server was refused.", file=sys.stderr)
        return False

def wait_for_server_ready(host, port, timeout=10):
    """Waits for the server to be ready by checking if the port is open."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
            debug(f"Server is ready on port {port}.")
            return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.1)
    print(f"Error: Timeout waiting for server to be ready on port {port}.", file=sys.stderr)
    return False

def run_client_benchmark():
    """Main function to run the client-side performance benchmark."""
    setup_results_dir()
    output_file = generate_output_filename()

    perf_command_base = [
        "perf", "stat", "-e", ",".join(config.PERF_EVENTS)
    ]
    client_connection_command = [config.CLIENT_COMMAND] + config.CLIENT_ARGS
    full_perf_command = perf_command_base + ["--"] + client_connection_command

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["iteration"] + config.PERF_EVENTS)
        
        for i in range(config.ITERATIONS):
            print(f"\n--- Starting Iteration {i} ---")

            if not wait_for_server_ready(config.SIGNAL_SSH_HOST, config.PORT_TO_CHECK):
                continue

            # Measure the performance of the client's SSH connection.
            print("Running perf on the client...")
            perf_output, return_code = execute_perf_on_client(full_perf_command)

            # Signal the server to stop
            signal_server()

            # A non-zero return code from SSH might be expected if the server
            # shuts down the connection very quickly after the command is sent.
            # We can consider the operation successful if perf ran.
            if "Timeout" in perf_output:
                 print(f"Client measurement timed out. Retrying...")
                 continue

            print("Client measurement captured!")
            metrics = parse_perf_output(perf_output)
            metrics["iteration"] = i
            row = [metrics["iteration"]] + [metrics[event] for event in config.PERF_EVENTS]
            writer.writerow(row)

            print(f"--- Finished Iteration {i} ---")

if __name__ == "__main__":
    # Set up signal handlers for graceful exit
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    print(f"Starting client tests. Results will be saved to: {generate_output_filename()}")
    run_client_benchmark()
