#!/usr/bin/python3

import subprocess
import csv
import sys
import os
import datetime
import socket
import time
import signal
import psutil
import config

def debug(msg):
    """Prints a debug message if DEBUG_MODE is True."""
    if config.DEBUG_MODE:
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
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

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

    config_path = get_config_from_args(config.SERVER_ARGS)
    config_filename = os.path.basename(config_path) if config_path else "generic"

    hostname = socket.gethostname()
    return os.path.join(config.RESULTS_DIR, f"{hostname}-{timestamp}-server-{config_filename}.csv")

def parse_perf_output(output):
    """Parses the stderr output from 'perf stat' to extract metrics."""
    metrics = {event: 0 for event in config.PERF_EVENTS}
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
    if is_port_in_use(config.PORT_TO_CHECK):
        print(f"Error: Port {config.PORT_TO_CHECK} is already in use.", file=sys.stderr)
        sys.exit(1)

    setup_results_dir()

    # Ensure no old signal file is present
    if os.path.exists(config.SIGNAL_FILE):
        os.remove(config.SIGNAL_FILE)

    perf_command = [
        "perf", "stat", "-e", ",".join(config.PERF_EVENTS)
    ]

    server_command = [config.SERVER_BINARY] + config.SERVER_ARGS

    try:
        print(f"Starting server binary '{config.SERVER_BINARY}'...")
        server_process = subprocess.Popen(server_command)
        debug(f"Server process started with PID: {server_process.pid}")

        time.sleep(1) # Give the server a moment to start

        perf_command = [
            "perf", "stat", "-e", ",".join(config.PERF_EVENTS),
            "-p", str(server_process.pid)
        ]

        debug(f"Running command: {' '.join(perf_command)}")
        perf_process = subprocess.Popen(perf_command, stderr=subprocess.PIPE, text=True)

        # Wait for a signal on the signaling port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', config.SIGNAL_PORT))
            s.listen()
            debug(f"Listening for signal on port {config.SIGNAL_PORT}")
            conn, addr = s.accept()
            with conn:
                debug(f"Signal received from {addr}")

        print("\n[INFO] Signal received to stop the server.")

        # Stop the perf process and the server process
        perf_process.send_signal(signal.SIGINT)
        server_process.kill()

        # Wait for the parent 'perf' process to terminate and capture its output
        stderr_output = perf_process.stderr.read()
        perf_process.wait(timeout=10)
        debug(f"Final perf stderr output:\n{stderr_output}")

        # Parse the perf output and save to CSV
        output_file = generate_output_filename()
        with open(output_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(config.PERF_EVENTS)
            metrics = parse_perf_output(stderr_output)
            row = [metrics[event] for event in config.PERF_EVENTS]
            writer.writerow(row)
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
        print("Server has shut down.")

if __name__ == "__main__":
    run_server_benchmark()

    