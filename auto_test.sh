#!/bin/bash

CONFIG_DIR="./config_files"
LINK_NAME="config.py"

echo "======================================"
echo "Using config directory: $CONFIG_DIR"
echo "Symlink target name:    $LINK_NAME"
echo "======================================"
echo

for config_file in "$CONFIG_DIR"/*; do
    echo "--------------------------------------"
    echo ">>> Processing: $config_file"
    echo "--------------------------------------"

    # Remove previous symlink or file if it exists
    if [ -L "$LINK_NAME" ] || [ -f "$LINK_NAME" ]; then
        rm -f "$LINK_NAME"
    fi

    # Create new symlink pointing to the current config file
    ln -s "$config_file" "$LINK_NAME"
    echo "Created symlink: $LINK_NAME -> $config_file"

    # Execute the desired script (uncomment only one of the lines below)
    ./run_server_loop.sh
    # ./run_client_loop.sh

    # Wait for user confirmation before continuing
    echo
    echo "=== Execution finished for $config_file ==="
    echo "Press ENTER to continue to the next one..."
    read -r
    echo
done

echo "======================================"
echo "All configuration files have been processed."
echo "======================================"
