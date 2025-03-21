"""
PyMOL-Claude Integration Plugin with MCP Server

This module provides MCP integration between PyMOL and Claude AI.
It allows Claude to visualize and manipulate molecular structures in PyMOL.

Author: Andre Watson (@nanogenomic)
Version: 0.1.0
"""

import os
import sys
import json
import socket
import threading
import time
from io import StringIO

# Import PyMOL modules
from pymol import cmd

# MCP server settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8090
BUFFER_SIZE = 4096

class ClaudePlugin:
    """
    Plugin class for PyMOL-Claude integration with MCP server functionality
    """
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """Initialize the plugin"""
        self.version = "0.1.0"
        self.author = "Andre Watson (@nanogenomic)"
        self.host = host
        self.port = port
        
        # MCP server variables
        self.server_thread = None
        self.running = False
        self.server_socket = None
    
    def __call__(self):
        """Called when the 'claude' command is executed in PyMOL"""
        print("\nClaude-PyMOL Integration")
        print("------------------------")
        print(f"Version: {self.version}")
        print(f"Author: {self.author}\n")
        
        print("This plugin enables Claude to control PyMOL via MCP.")
        print("Claude can execute commands and manipulate molecular structures.\n")
        
        # Show MCP server status
        print("MCP Server Status:", "Running" if self.running else "Stopped")
        if self.running:
            print(f"Listening on {self.host}:{self.port}")
        else:
            print("Use 'claude_start_server' to start the MCP server")
        
        # Register additional commands
        if not hasattr(cmd, 'claude_start_server'):
            cmd.extend('claude_start_server', self.start_mcp_server)
            cmd.extend('claude_stop_server', self.stop_mcp_server)
            print("\nAvailable commands:")
            print("  claude_start_server - Start the MCP server")
            print("  claude_stop_server  - Stop the MCP server")
    
    def handle_mcp_request(self, request):
        """
        Handle an MCP request from Claude
        
        Args:
            request: The MCP request from Claude
            
        Returns:
            The response to send back to Claude
        """
        try:
            # Parse the request
            if isinstance(request, str):
                try:
                    # Try to parse as JSON
                    req_data = json.loads(request)
                except json.JSONDecodeError:
                    # Treat as direct command if not valid JSON
                    req_data = {
                        "type": "execute_command",
                        "command": request
                    }
            else:
                req_data = request
            
            # Process different request types
            req_type = req_data.get("type", "execute_command")
            
            if req_type == "execute_command" or req_type == "direct_input":
                # Execute PyMOL command
                command = req_data.get("command", "") or req_data.get("text", "")
                if command:
                    result = self._execute_pymol_command(command)
                    return {
                        "status": "success",
                        "message": "Command executed",
                        "data": result
                    }
            
            elif req_type == "get_state":
                # Get PyMOL state information
                result = self._get_pymol_state()
                return {
                    "status": "success",
                    "message": "State retrieved",
                    "data": result
                }
            
            elif req_type == "ping":
                # Simple ping to check connection
                return {
                    "status": "success",
                    "message": "PyMOL MCP server is connected",
                    "data": {
                        "version": self.version,
                        "pymol_version": cmd.get_version()[0],
                        "author": self.author
                    }
                }
            
            elif req_type == "edit_pdb":
                # Edit a PDB file
                file_path = req_data.get("file", "")
                content = req_data.get("content", "")
                if file_path and content:
                    result = self._edit_pdb_file(file_path, content)
                    return {
                        "status": "success",
                        "message": "PDB file edited",
                        "data": result
                    }
            
            elif req_type == "get_pdb_content":
                # Get PDB file content
                file_path = req_data.get("file", "")
                if file_path:
                    result = self._get_pdb_content(file_path)
                    return {
                        "status": "success",
                        "message": "PDB content retrieved",
                        "data": result
                    }
            
            elif req_type == "list_pdb_files":
                # List PDB files
                directory = req_data.get("directory", "")
                result = self._list_pdb_files(directory)
                return {
                    "status": "success",
                    "message": "PDB files listed",
                    "data": result
                }
            
            # Unknown request type
            return {
                "status": "error",
                "message": f"Unknown request type: {req_type}",
                "data": None
            }
            
        except Exception as e:
            # Handle any exceptions
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }
    
    def start_mcp_server(self):
        """Start the MCP server in a separate thread"""
        if self.running:
            print(f"MCP server is already running on {self.host}:{self.port}")
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"MCP server started on {self.host}:{self.port}")
        print("Claude can now connect to PyMOL")
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if not self.running:
            print("MCP server is not running")
            return
        
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("MCP server stopped")
    
    def _run_server(self):
        """Run the MCP server loop"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # 1 second timeout to check running flag
            
            print(f"MCP server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client, addr = self.server_socket.accept()
                    self._handle_client(client)
                except socket.timeout:
                    # This is expected due to the timeout
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def _handle_client(self, client_socket):
        """Handle a client connection"""
        try:
            data = b""
            
            # Receive data
            while True:
                chunk = client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                
                data += chunk
                
                # End of message marker
                if b"\n\n" in data:
                    break
            
            if not data:
                return
            
            # Process the request
            try:
                # Parse JSON request
                request_str = data.decode('utf-8').strip()
                response = self.handle_mcp_request(request_str)
                
                # Send response
                response_json = json.dumps(response)
                client_socket.sendall(response_json.encode('utf-8'))
                
            except json.JSONDecodeError:
                # Handle invalid JSON
                error_response = {
                    "status": "error",
                    "message": "Invalid JSON request",
                    "data": None
                }
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client connection: {e}")
        finally:
            client_socket.close()
    
    def _execute_pymol_command(self, command_str):
        """Execute a PyMOL command and return the result"""
        try:
            # Capture PyMOL output
            old_stdout = sys.stdout
            sys.stdout = output = StringIO()
            
            # Execute the command
            result = cmd.do(command_str)
            
            # Get the output
            output_text = output.getvalue()
            
            # Restore stdout
            sys.stdout = old_stdout
            
            return {
                "result": result,
                "output": output_text
            }
        except Exception as e:
            return {
                "result": None,
                "output": f"Error: {str(e)}"
            }
    
    def _get_pymol_state(self):
        """Get current PyMOL state information"""
        try:
            state_info = {
                "loaded_objects": cmd.get_names('objects'),
                "current_view": cmd.get_view(),
                "selections": cmd.get_names('selections')
            }
            return state_info
        except Exception as e:
            return {
                "error": f"Error getting PyMOL state: {str(e)}"
            }
    
    def _edit_pdb_file(self, pdb_file, pdb_content):
        """Edit a PDB file with the provided content"""
        try:
            # Check if file is already loaded in PyMOL
            loaded_objects = cmd.get_names('objects')
            file_base = os.path.basename(pdb_file)
            file_name = os.path.splitext(file_base)[0]
            
            # Determine file path
            if os.path.isabs(pdb_file):
                # Absolute path provided
                file_path = pdb_file
            else:
                # Use current working directory
                cwd = os.getcwd()
                file_path = os.path.join(cwd, pdb_file)
            
            # Write the new content to the file
            with open(file_path, 'w') as f:
                f.write(pdb_content)
            
            # If the object was loaded, reload it
            if file_name in loaded_objects:
                cmd.load(file_path, file_name, format='pdb', state=1)
                reload_message = f"Reloaded PDB file '{file_name}'"
            else:
                reload_message = "File edited but not reloaded (not currently loaded in PyMOL)"
            
            return {
                "path": file_path,
                "message": reload_message
            }
        except Exception as e:
            return {
                "error": f"Error editing PDB file: {str(e)}"
            }
    
    def _get_pdb_content(self, pdb_file):
        """Get the content of a PDB file"""
        try:
            # Determine file path
            if os.path.isabs(pdb_file):
                # Absolute path provided
                file_path = pdb_file
            else:
                # Use current working directory
                cwd = os.getcwd()
                file_path = os.path.join(cwd, pdb_file)
            
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            return {
                "path": file_path,
                "content": content
            }
        except Exception as e:
            return {
                "error": f"Error reading PDB file: {str(e)}"
            }
    
    def _list_pdb_files(self, directory=None):
        """List PDB files in the specified directory"""
        try:
            # Determine directory path
            if directory:
                if os.path.isabs(directory):
                    dir_path = directory
                else:
                    cwd = os.getcwd()
                    dir_path = os.path.join(cwd, directory)
            else:
                dir_path = os.getcwd()
            
            # List PDB files
            pdb_files = []
            for file in os.listdir(dir_path):
                if file.lower().endswith(('.pdb', '.cif')):
                    file_path = os.path.join(dir_path, file)
                    pdb_files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path)
                    })
            
            return {
                "directory": dir_path,
                "files": pdb_files
            }
        except Exception as e:
            return {
                "error": f"Error listing PDB files: {str(e)}"
            }