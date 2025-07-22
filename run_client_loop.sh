#!/bin/bash
#
# This wrapper script runs a target client script (e.g., client_perf.py)
# in a loop. It's designed to work with a client that signals the client
# script to stop, allowing for iterative measurements.
# --- FIX KEY PERMISSION ---
chmod 600 client_keys/*

# --- CONFIGURATION ---
# The client script to run in a loop.
CLIENT_SCRIPT="./client_perf.py"
# Number of times to loop.
LOOP_COUNT=$(python3 -c "import config; print(config.ITERATIONS)")

echo "Starting the client loop for '$CLIENT_SCRIPT'..."
$CLIENT_SCRIPT
echo "Client loop finished."
