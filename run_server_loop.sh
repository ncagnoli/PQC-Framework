#!/bin/bash
#
# This wrapper script runs a target server script (e.g., server_perf.py)
# in a loop. It's designed to work with a client that signals the server
# script to stop, allowing for iterative measurements.
# --- FIX KEY PERMISSION ---
chmod 600 server_keys/*

# --- CONFIGURATION ---
# The server script to run in a loop.
SERVER_SCRIPT="./server_perf.py"
# Number of times to loop.
LOOP_COUNT=$(python3 -c "import config; print(config.ITERATIONS)")

echo "Starting the server loop for '$SERVER_SCRIPT'..."
for (( i=1; i<=LOOP_COUNT; i++ ))
do
    echo "--- Starting server script, iteration $i ---"
    $SERVER_SCRIPT

    # The server script is expected to exit with 0 when signaled by the client.
    # A non-zero exit code indicates an actual error, so we stop the loop.
    if [ $? -ne 0 ]; then
        echo "Server script exited with a non-zero status. Stopping the loop."
        break
    fi

    echo "--- Server script finished. Restarting in .5 seconds... ---"
    sleep .3
done
echo "Server loop finished."
