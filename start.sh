#!/bin/sh

# Ensure config folder exists
mkdir -p /config

# Copy example config if no config exists
if [ ! -f /app/config/CONFIG.yaml ]; then
    echo "CONFIG.yaml not found; creating from CONFIG_EXAMPLE.yaml"
    cp /app/CONFIG_EXAMPLE.yaml /config/CONFIG.yaml
fi

echo "===== Environment Variables ====="
printenv
echo "================================="

# Main loop
while true; do
    python -m soulbrainarr
    sleep "${RUN_INTERVAL:-600}"
done
