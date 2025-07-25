#!/bin/bash
"""
Seneca Installation Script

Installs the 'seneca' command for easy system-wide access.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}Seneca Installation${NC}"
echo "==================="
echo

# Check if running as root for /usr/local/bin
if [ "$EUID" -eq 0 ]; then 
    INSTALL_DIR="/usr/local/bin"
else
    # Install to user's local bin
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo -e "${YELLOW}Warning: $INSTALL_DIR is not in your PATH${NC}"
        echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo
    fi
fi

# Create symlink
echo "Installing seneca command to $INSTALL_DIR..."
ln -sf "$SCRIPT_DIR/seneca" "$INSTALL_DIR/seneca"

# Check Python dependencies
echo
echo "Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Warning: Flask not found${NC}"
    echo "Install dependencies with: pip install -r requirements.txt"
fi

# Create directories
mkdir -p "$HOME/.seneca/logs"

echo
echo -e "${GREEN}✅ Seneca installed successfully!${NC}"
echo
echo "Usage:"
echo "  seneca start       # Start Seneca server"
echo "  seneca open        # Open in browser"
echo "  seneca status      # Check if running"
echo "  seneca stop        # Stop server"
echo "  seneca --help      # Show all commands"
echo
echo "Quick start:"
echo "  seneca start                      # Auto-discover Marcus"
echo "  seneca start --marcus-http URL    # Connect to specific Marcus"
echo