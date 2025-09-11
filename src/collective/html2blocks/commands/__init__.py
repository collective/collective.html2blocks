"""Command Line Interface for html2blocks.

CLI commands package for collective.html2blocks.

This package provides Typer-based command modules for converting HTML files,
inspecting tool information, and running the API server.

Available commands:
    - convert: Convert HTML files to Volto blocks JSON
    - info: Show tool and converter registration information
    - server: Run the HTML to Blocks API service

Example usage::

    $ uv run html2blocks convert input.html output.json
    $ uv run html2blocks info
    $ uv run html2blocks server --host 0.0.0.0 --port 8080
"""
