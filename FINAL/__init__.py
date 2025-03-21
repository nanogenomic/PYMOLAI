# PyMOL plugin initialization for Claude MCP Integration
# Author: Andre Watson (@nanogenomic)

def __init_plugin__(app=None):
    from pymol import cmd
    import sys
    import os
    
    # Add the plugin directory to Python path
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    if plugin_dir not in sys.path:
        sys.path.append(plugin_dir)
    
    # Import and initialize the plugin
    try:
        # Import the main plugin module
        import pymol_claude
        
        # Create plugin instance
        plugin = pymol_claude.ClaudePlugin()
        
        # Register PyMOL commands
        cmd.extend('claude', lambda: plugin())
        cmd.extend('claude_start_server', plugin.start_mcp_server)
        cmd.extend('claude_stop_server', plugin.stop_mcp_server)
        
        # Auto-start the MCP server
        plugin.start_mcp_server()
        
        # Log successful initialization
        print("\nClaude Integration Plugin loaded successfully")
        print("MCP server started automatically")
        print("Use 'claude' command for more information")
        
    except ImportError as e:
        print(f"Error loading Claude Integration Plugin: {e}")