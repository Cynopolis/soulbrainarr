#!/bin/sh

# Ensure config folder exists
mkdir -p /config

# Copy example config if no config exists
if [ ! -f "${CONFIG_PATH}" ]; then
    echo "${CONFIG_PATH} not found; creating from CONFIG_EXAMPLE.yaml"
    cp /app/CONFIG_EXAMPLE.yaml "${CONFIG_PATH}"
fi

echo "===== Environment Variables ====="
printenv
echo "================================="

# Main loop
while true; do
    python -m soulbrainarr
    sleep "${RUN_INTERVAL:-600}"
done
