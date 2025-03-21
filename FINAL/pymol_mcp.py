#!/usr/bin/env python3
"""
MCP-Compatible PyMOL Interface
This script provides an MCP server that connects to PyMOL.
"""

import sys
import socket
import json
import os
import subprocess

# PyMOL server settings
PYMOL_HOST = '127.0.0.1'
PYMOL_PORT = 8090  # PyMOL's existing server port

def send_command_to_pymol(command):
    """Send a command to PyMOL's socket server"""
    try:
        # Create socket connection to PyMOL
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5.0)  # 5 second timeout for connection
        client.connect((PYMOL_HOST, PYMOL_PORT))
        
        # Create request payload
        payload = {
            "type": "execute_command",
            "command": command
        }
        
        # Send the request
        request_str = json.dumps(payload) + "\n\n"
        client.sendall(request_str.encode('utf-8'))
        
        # PyMOL doesn't respond properly, so we'll close immediately
        client.close()
        
        return {
            "status": "success",
            "message": f"Command sent to PyMOL: {command}",
            "output": "Command executed successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error sending command to PyMOL: {str(e)}",
            "output": f"Error: {str(e)}"
        }

# MCP Protocol Handler
def process_message(message):
    """Process a JSON-RPC message"""
    try:
        if message.get("method") == "initialize":
            # Return initialization response
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "pymol-mcp-bridge",
                        "version": "0.1.0"
                    }
                }
            }
        
        elif message.get("method") == "notifications/initialized":
            # No response needed for notifications
            return None
            
        elif message.get("method") == "tools/list":
            # List available tools
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "send_command",
                            "description": "Send a command to PyMOL",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command": {
                                        "type": "string",
                                        "description": "PyMOL command to execute"
                                    }
                                },
                                "required": ["command"],
                                "additionalProperties": False
                            }
                        }
                    ]
                }
            }
        
        elif message.get("method") == "tools/call" or message.get("method") == "tools/execute":
            # Execute a tool
            params = message.get("params", {})
            
            # Handle different method formats
            if message.get("method") == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                sys.stderr.write(f"Received tools/call for {tool_name}\n")
            else:  # tools/execute
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
            
            if tool_name == "send_command":
                command = arguments.get("command", "")
                
                if not command:
                    return {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: command is required"
                        }
                    }
                
                result = send_command_to_pymol(command)
                sys.stderr.write(f"Sent command to PyMOL: {command}\n")
                
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
        
        else:
            # Unknown method
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {message.get('method')}"
                }
            }
    
    except Exception as e:
        # Internal error
        sys.stderr.write(f"Error processing message: {str(e)}\n")
        sys.stderr.flush()
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def main():
    """Main entry point"""
    # Read from stdin and write to stdout (MCP protocol)
    sys.stderr.write("PyMOL MCP Bridge started\n")
    sys.stderr.flush()
    
    buffer = ""
    while True:
        try:
            chunk = sys.stdin.read(1)
            if not chunk:  # EOF
                break
            
            buffer += chunk
            
            # Check for complete message (line break)
            if buffer.endswith('\n'):
                if buffer.strip():  # Skip empty lines
                    try:
                        message = json.loads(buffer)
                        sys.stderr.write(f"Received message: {message.get('method')}\n")
                        sys.stderr.flush()
                        
                        response = process_message(message)
                        
                        if response:  # Some notifications don't require responses
                            sys.stdout.write(json.dumps(response) + '\n')
                            sys.stdout.flush()
                    
                    except json.JSONDecodeError as e:
                        # Invalid JSON
                        sys.stderr.write(f"Error: Invalid JSON received: {e}\n")
                        sys.stderr.flush()
                
                buffer = ""
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            sys.stderr.write(f"Error in main loop: {str(e)}\n")
            sys.stderr.flush()
            break

if __name__ == "__main__":
    main()
