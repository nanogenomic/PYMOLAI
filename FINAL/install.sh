#!/bin/bash
# Installation script for PyMOL-Claude Integration

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}PyMOL-Claude Integration Installer${NC}"
echo "==============================================="
echo ""

# Get the username
USERNAME=$(whoami)
echo -e "${YELLOW}Detected username:${NC} $USERNAME"

# Get the current directory
INSTALL_DIR=$(pwd)
echo -e "${YELLOW}Installation directory:${NC} $INSTALL_DIR"

# Create PyMOL plugins directory if it doesn't exist
PYMOL_PLUGIN_DIR="/Users/$USERNAME/.pymol/plugins"
if [ ! -d "$PYMOL_PLUGIN_DIR" ]; then
    echo -e "${YELLOW}Creating PyMOL plugins directory...${NC}"
    mkdir -p "$PYMOL_PLUGIN_DIR"
fi

# Create Claude integration plugin directory
CLAUDE_PLUGIN_DIR="$PYMOL_PLUGIN_DIR/claude_integration"
if [ -d "$CLAUDE_PLUGIN_DIR" ]; then
    echo -e "${YELLOW}Backing up existing Claude plugin...${NC}"
    mv "$CLAUDE_PLUGIN_DIR" "$CLAUDE_PLUGIN_DIR.bak"
fi

echo -e "${YELLOW}Installing Claude plugin to PyMOL...${NC}"
mkdir -p "$CLAUDE_PLUGIN_DIR"
cp -r claude_plugin/* "$CLAUDE_PLUGIN_DIR/"

# Make the MCP script executable
echo -e "${YELLOW}Making MCP script executable...${NC}"
chmod +x "$INSTALL_DIR/pymol_mcp.py"

# Update Claude Desktop configuration
CLAUDE_CONFIG_DIR="/Users/$USERNAME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo -e "${YELLOW}Backing up existing Claude configuration...${NC}"
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.bak"
fi

# Create Claude configuration directory if it doesn't exist
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo -e "${YELLOW}Creating Claude configuration directory...${NC}"
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Generate a new configuration with the correct paths
echo -e "${YELLOW}Updating Claude configuration...${NC}"
cat claude_desktop_config.template.json | sed "s|/Users/USERNAME|/Users/$USERNAME|g" | sed "s|PATH_TO_INSTALLATION|$INSTALL_DIR|g" > "$CLAUDE_CONFIG_FILE"

echo ""
echo -e "${GREEN}Installation Complete!${NC}"
echo "==============================================="
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start PyMOL"
echo "2. Start Claude Desktop"
echo "3. In Claude, test the integration by sending a command:"
echo "   fetch 1cbs"
echo "   show cartoon"
echo "   color spectrum"
echo ""
echo -e "${YELLOW}If you encounter any issues:${NC}"
echo "- Check the terminal output for error messages"
echo "- Verify that PyMOL is running with the plugin active"
echo "- Make sure Claude Desktop is properly configured"
echo "- Try restarting both PyMOL and Claude Desktop"
echo ""
echo "Enjoy using PyMOL-Claude Integration!"
