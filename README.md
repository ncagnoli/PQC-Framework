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

All configuration has been centralized in the `config.py` file. Open this file to adjust all parameters for your benchmark.

### Key Configuration Variables in `config.py`

- **General Settings**:
  - `ITERATIONS`: The number of benchmark iterations to run.
  - `DEBUG_MODE`: Set to `True` to see verbose output from the scripts.

- **Server Settings**:
  - `SERVER_BINARY`: The absolute path to the server executable (e.g., `/usr/sbin/sshd`).
  - `SERVER_ARGS`: A list of command-line arguments for the server binary.
  - `PORT_TO_CHECK`: The port the server will use.

- **Client Settings**:
  - `CLIENT_COMMAND`: The client executable to run (e.g., `ssh`).
  - `CLIENT_ARGS`: A list of arguments for the client command. By default, this includes the `REMOTE_COMMAND` which signals the server.
  - `TEST_NAME`: A friendly name for your test, used in the output filename.

- **Signaling**:
  - `SIGNAL_SSH_*`: SSH connection details (`USER`, `HOST`, `PORT`, `KEY`) used by the client to connect to the server. **This requires passwordless SSH access (e.g., via public key authentication) to be configured for the specified user.**

## How to Run

1.  **Set Script Permissions**: Ensure all scripts are executable:
    ```bash
    chmod +x run_server_loop.sh server_perf.py client_perf.py
    ```

2.  **Configure `config.py`**: Adjust the settings in `config.py` for your specific test case (e.g., server binary, arguments, SSH keys). Ensure you have passwordless SSH access to the server from the client machine.

3.  **Start the Server Loop**: In a terminal on the server machine, run the wrapper script. It will wait for the client to start the process.
    ```bash
    ./run_server_loop.sh
    ```

4.  **Run the Client Benchmark**: In a separate terminal (on the client machine), run the client script. This will create the session ID and kick off the benchmark iterations.
    ```bash
    ./client_perf.py
    ```

5.  **Monitor the Output**: You will see progress printed in both terminals as the client and server interact.

6.  **Collect Results**: Once the client script finishes its iterations, you can stop the server loop with `CTRL+C`. Two CSV files (one for the server, one for the client) containing all iteration data will be in the `Results/` directory.
