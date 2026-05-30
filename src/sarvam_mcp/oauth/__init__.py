"""OAuth 2.1 authorization server endpoints.

Implements RFC 9728 (protected resource metadata) and dynamic client
registration so MCP clients (Cursor, Claude Desktop) can discover auth
requirements and prompt the user to log in via browser.
"""
