#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./scripts/install.sh"
    exit 1
fi

REAL_USER=${SUDO_USER:-$(whoami)}
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_NAME="rpi-system-info"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TEMPLATE_FILE="$(dirname "$0")/${SERVICE_NAME}.service"

# If UV_PATH is not set externally, try to find it automatically
if [ -z "$UV_PATH" ]; then
    # Try to find uv in the real user's PATH (non‑interactive)
    UV_PATH=$(sudo -u "$REAL_USER" bash -c 'command -v uv' 2>/dev/null || echo "")
    if [ -z "$UV_PATH" ]; then
        # Check common installation directories
        for candidate in "/home/$REAL_USER/.local/bin/uv" \
                         "/usr/bin/uv" \
                         "/usr/local/bin/uv" \
                         "/home/$REAL_USER/.cargo/bin/uv"; do
            if [ -x "$candidate" ]; then
                UV_PATH="$candidate"
                break
            fi
        done
    fi
fi

# Verify that the binary exists and is executable
if [ ! -x "$UV_PATH" ]; then
    echo "Error: uv not found or not executable (tried: $UV_PATH)."
    echo "Please install uv or set the UV_PATH environment variable to a valid uv binary."
    exit 1
fi

echo "Installing service $SERVICE_NAME"
echo "Project: $PROJECT_DIR"
echo "User: $REAL_USER"
echo "uv: $UV_PATH"

# Substitute placeholders in the template and install the unit file
sed -e "s|{{USER}}|$REAL_USER|g" \
    -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
    -e "s|{{UV_PATH}}|$UV_PATH|g" \
    "$TEMPLATE_FILE" > "$SERVICE_FILE"

echo "Unit file created: $SERVICE_FILE"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Service successfully installed and started."
echo "Check status: sudo systemctl status $SERVICE_NAME"
