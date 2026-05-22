"""Self-contained OAuth 2.1 authorization server for MCP clients.

Implements RFC 9728 (OAuth Protected Resource Metadata) and dynamic client
registration so MCP clients (Cursor, Claude Desktop) can discover auth
requirements and prompt the user for their Sarvam API key via browser.
"""
