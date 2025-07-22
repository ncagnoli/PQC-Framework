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
for (( i=1; i<=LOOP_COUNT; i++ ))
do
    echo "--- Starting client script, iteration $i ---"
    $CLIENT_SCRIPT

    # The client script is expected to exit with 0 when signaled by the client.
    # A non-zero exit code indicates an actual error, so we stop the loop.
    if [ $? -ne 0 ]; then
        echo "Client script exited with a non-zero status. Stopping the loop."
        break
    fi

    echo "--- Client script finished. Restarting in .5 seconds... ---"
    sleep .3
done
echo "Client loop finished."
