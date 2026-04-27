#!/bin/bash
# Send a minimal MCP handshake + tools/list and print the tool names.
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
  echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
  sleep 1
} | timeout 4 "$1" 2>/dev/null | python3 -c "
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        msg = json.loads(line)
    except Exception:
        continue
    if msg.get('id') == 2 and 'result' in msg:
        tools = msg['result'].get('tools', [])
        print(f'tools/list returned {len(tools)} tools:')
        for t in sorted(tools, key=lambda x: x['name']):
            print(f'  - {t[\"name\"]}')
"
