MOLAI v0.1.0

# PyMOL-Claude Integration

A direct integration between Claude AI and PyMOL molecular visualization software, enabling Claude to control and manipulate molecular structures in PyMOL.

## Overview

This project provides a seamless integration between Anthropic's Claude AI assistant and the PyMOL molecular visualization program. With this integration, you can:

- Send PyMOL commands directly from Claude
- Visualize and manipulate molecular structures
- Create complex molecular representations
- Automate PyMOL workflows through natural language

## Components

The integration consists of three main components:

1. **MCP Server Script** - A script that handles Model Context Protocol (MCP) communication between Claude and PyMOL
2. **PyMOL Plugin** - A plugin for PyMOL that enables direct communication with Claude
3. **Claude Desktop Configuration** - Configuration for Claude Desktop to connect to the MCP server

## Quick Start

For a quick deployment, use the files in the `FINAL` directory:

1. Copy the `pymol_mcp.py` script to a location accessible to Claude Desktop
2. Copy the `claude_plugin` directory to your PyMOL plugins directory, or go to Plugin -> Plugin Manager to load the __init__.py and pymol_claude.py files
3. Update your Claude Desktop configuration to point to the MCP script, and update the filesystem paths as appropriate.
4. Start PyMOL and then start Claude Desktop

See the [FINAL/README.md](FINAL/README.md) for detailed deployment instructions.

## Examples

After setting up the integration, you can send commands to PyMOL directly from Claude:

```
fetch 1LG5
show cartoon
color spectrum
zoom
```

## Development

If you want to modify or extend the integration, see the development guide in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## License

This project is licensed under a hybrid MIT - Ligandal License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for developing Claude AI
- PyMOL developers for the powerful molecular visualization software
- This integration was created by Andre Watson (@nanogenomic)
