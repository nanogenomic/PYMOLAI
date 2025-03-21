# PyMOL-Claude Integration - Deployment

This directory contains everything needed for deploying the PyMOL-Claude integration.

## Installation

### 1. Install PyMOL Plugin

Copy the `claude_plugin` directory to your PyMOL plugins directory:

```bash
cp -r claude_plugin ~/.pymol/plugins/claude_integration
```

### 2. Configure Claude Desktop

1. Locate your Claude Desktop configuration file:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "pymol": {
         "command": "python3",
         "args": [
           "/path/to/pymol_mcp.py"
         ]
       }
     }
   }
   ```
   Replace `/path/to/pymol_mcp.py` with the full path to where you've placed the `pymol_mcp.py` file.

### 3. Start the Integration

1. Start PyMOL
2. The Claude plugin should automatically start in PyMOL
3. Start Claude Desktop

## Testing the Integration

To test if the integration is working:

1. In Claude, send a command to PyMOL:
   ```
   fetch 1cbs
   show cartoon
   color spectrum
   ```

2. You should see PyMOL respond by fetching and displaying the structure.

## Troubleshooting

If the integration doesn't work:

1. Check if PyMOL is running with the plugin active
2. Verify that Claude Desktop is properly configured
3. Check the terminal output for error messages
4. Try restarting both PyMOL and Claude Desktop

## File Descriptions

- `pymol_mcp.py` - The MCP server script that handles communication between Claude and PyMOL
- `claude_plugin/` - The PyMOL plugin that enables direct communication with Claude
  - `__init__.py` - Plugin initialization
  - `pymol_claude.py` - Main plugin implementation
