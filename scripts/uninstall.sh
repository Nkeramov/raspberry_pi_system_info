#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./scripts/uninstall.sh"
    exit 1
fi

SERVICE_NAME="rpi-system-info"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Service $SERVICE_NAME not found (file $SERVICE_FILE missing)."
    exit 0
fi

echo "Stopping and disabling service $SERVICE_NAME..."
systemctl stop "$SERVICE_NAME" || true
systemctl disable "$SERVICE_NAME" || true

echo "Removing $SERVICE_FILE..."
rm -f "$SERVICE_FILE"

echo "Reloading systemd..."
systemctl daemon-reload

echo "Service $SERVICE_NAME removed."
