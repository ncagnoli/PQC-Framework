#!/bin/bash
#
# This wrapper script runs a target server script (e.g., server_perf.py)
# in a loop. It's designed to work with a client that signals the server
# script to stop, allowing for iterative measurements.

# --- CONFIGURATION ---
SERVER_SCRIPT="./server_perf.py"
# Number of times to loop. Should be >= the client's ITERATIONS.
LOOP_COUNT=1500
# ---

echo "Starting the server loop for '$SERVER_SCRIPT'..."
for (( i=0; i<LOOP_COUNT; i++ ))
do
    echo "--- Starting server script, iteration $i ---"
    # Pass the current iteration number to the server script
    $SERVER_SCRIPT $i

    if [ $? -ne 0 ]; then
        echo "Server script exited with a non-zero status. Stopping the loop."
        break
    fi

    echo "--- Server finished iteration $i. Restarting in 2 seconds... ---"
    sleep 2
done

echo "Server loop finished."
