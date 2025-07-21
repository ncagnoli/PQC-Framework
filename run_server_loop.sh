#!/bin/bash
#
# This wrapper script runs a target server script (e.g., server_perf.py)
# in a loop. It's designed to work with a client that signals the server
# script to stop, allowing for iterative measurements.

# --- CONFIGURATION ---
SERVER_SCRIPT="./server_perf.py"
CLIENT_SCRIPT="./client_perf.py"
RESULTS_DIR="Results"
LOOP_COUNT=1500
# ---

# Generate a single timestamp for this entire benchmark run
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
SERVER_OUTPUT_FILE="$RESULTS_DIR/server-results-$TIMESTAMP.csv"
CLIENT_OUTPUT_FILE="$RESULTS_DIR/client-results-$TIMESTAMP.csv"

# Ensure the results directory exists
mkdir -p $RESULTS_DIR

echo "Benchmark run starting."
echo "Server results will be saved to: $SERVER_OUTPUT_FILE"
echo "Client results will be saved to: $CLIENT_OUTPUT_FILE"

# Launch the client script in the background, passing its output file
echo "Launching client script in the background..."
$CLIENT_SCRIPT $CLIENT_OUTPUT_FILE &
CLIENT_PID=$!

# Start the server loop
echo "Starting the server loop..."
for (( i=0; i<LOOP_COUNT; i++ ))
do
    echo "--- Starting server script, iteration $i ---"
    # Pass iteration number and the output file to the server script
    $SERVER_SCRIPT $i $SERVER_OUTPUT_FILE

    if [ $? -ne 0 ]; then
        echo "Server script exited with a non-zero status. Stopping the loop."
        # If the server fails, stop the client as well
        kill $CLIENT_PID 2>/dev/null
        break
    fi

    # Check if the client is still running before sleeping
    if ! ps -p $CLIENT_PID > /dev/null; then
        echo "Client script has finished. Ending server loop."
        break
    fi

    echo "--- Server finished iteration $i. Restarting in 2 seconds... ---"
    sleep 2
done

echo "Benchmark run finished."
