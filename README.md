# Perf Benchmark Toolkit

This toolkit provides a pair of Python scripts (`server_perf.py` and `client_perf.py`) for running iterative performance benchmarks on a server process using `perf stat`. It uses a client-server model where the client orchestrates the start and stop of measurements on both itself and the server, ensuring that data is captured for each transaction.

## Features

- **Iterative Benchmarking**: Run a client-server interaction a specified number of times and record performance metrics for each run.
- **Synchronized Measurements**: The client signals the server to stop its `perf` recording after each client measurement is complete.
- **Generic by Design**: While configured for SSH by default, the scripts can be easily adapted to benchmark other server binaries and client interactions.
- **CSV Output**: Saves performance data (cycles, instructions, cache misses, etc.) in separate, timestamped CSV files for the client and server.

## How It Works

The system is composed of three main components:

1.  **`server_perf.py`**: This script wraps a target server binary (e.g., `/usr/sbin/sshd`) with the `perf stat` command. It starts the server and then waits. It continuously checks for the existence of a "signal file" (`/tmp/stop_server_perf`). When this file is detected, the script sends a `SIGINT` to the `perf` process, causing it to terminate gracefully, print its results, and exit. The script then parses the `perf` output and saves it to a CSV file.

2.  **`run_server_loop.sh`**: Since `server_perf.py` is designed to exit after each measurement, this shell script runs it in a loop. When the server script exits, the loop waits a moment and then restarts it, making it ready for the next client connection.

3.  **`client_perf.py`**: This is the orchestrator. For each iteration, it performs the following steps:
    a. Removes the signal file on the server via SSH to ensure the server is running and ready.
    b. Waits a few seconds for the server to initialize.
    c. Runs its own client command (e.g., an `ssh` connection) under `perf stat`.
    d. Saves its own performance results to a CSV file.
    e. Creates the signal file on the server via SSH, which tells `server_perf.py` to stop and save its results.

This cycle repeats for the configured number of iterations.

## Setup and Configuration

### Server (`server_perf.py`)

Open `server_perf.py` and edit the `SETTINGS` section:

- `SERVER_BINARY`: The absolute path to the server executable you want to benchmark (e.g., `/usr/sbin/sshd`, `/usr/sbin/nginx`).
- `SERVER_ARGS`: A list of command-line arguments for the server binary.
- `SERVER_CONFIG_FILE`: (Optional) Path to a config file, used for generating a descriptive output filename.
- `PORT_TO_CHECK`: (Optional) A port number to check for availability before starting the server. Set to `None` to disable the check.

### Client (`client_perf.py`)

Open `client_perf.py` and edit the `SETTINGS` section:

- `ITERATIONS`: The number of benchmark iterations to run.
- `CLIENT_COMMAND`: The client executable to run (e.g., `ssh`, `curl`).
- `CLIENT_ARGS`: A list of arguments for the client command. This command should interact with the server.
- `TEST_NAME`: A friendly name for the test, used in the output filename.
- `SIGNAL_SSH_*` variables: These settings (`SIGNAL_SSH_USER`, `SIGNAL_SSH_HOST`, etc.) are used to connect to the server to create and remove the signal file. **This requires passwordless SSH access (e.g., via public key authentication) to be configured for the specified user.**

## How to Run

1.  **Configure the scripts** as described above. Ensure you have passwordless SSH access from the client machine to the server machine if they are different.

2.  **Start the Server Loop**: Open a terminal on the server machine and run the wrapper script.
    ```bash
    chmod +x run_server_loop.sh
    ./run_server_loop.sh
    ```
    The script will start `server_perf.py`, which will wait for a client connection.

3.  **Run the Client Benchmark**: Open another terminal (on the client machine, if applicable) and run the client script.
    ```bash
    ./client_perf.py
    ```

4.  **Monitor the Output**: You will see progress printed in both terminals as the client and server interact for each iteration.

5.  **Collect Results**: Once the client script finishes, all performance data will be available in the `Results/` directory on their respective machines. The server loop can be stopped with `CTRL+C`.
