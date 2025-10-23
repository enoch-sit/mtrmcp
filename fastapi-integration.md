Yes, it is possible to serve the MCP server under the `/mcp` directory using FastAPI (assuming FastMCP is built on or compatible with FastAPI/ASGI, which it appears to be based on its SSE transport). However, since the provided script uses `FastMCP` to run a standalone SSE server (with the endpoint at `/sse` by default), we need to make some adjustments:

1. **Run the MCP server on a dedicated port**: Keep the script running as a standalone server (e.g., on port 8000 or a different port like 8001 to avoid conflicts). No major code changes are needed if FastMCP doesn't support direct mounting in another FastAPI app. If FastMCP exposes an ASGI app (e.g., via `mcp.app`), you could mount it in a custom FastAPI app, but based on the code, it seems designed for standalone use.

2. **Update NGINX config**: Add a new `location /mcp` block that proxies requests to the MCP server's SSE endpoint. This effectively "mounts" the service under `/mcp` without changing the backend path. Use similar proxy settings as your existing `/langgraphplayground/` location to handle streaming (SSE requires buffering off and proper timeouts).

3. **Optional script tweak**: If FastMCP's `run()` method allows customizing the port or path, use it. Otherwise, run as-is.

### Step 1: Modify the Python Script (Minimal Changes)
Add a `port` parameter to `mcp.run()` if supported (check FastMCP docs; if not, default to 8000). For safety, run on a free port like 8001. No need to integrate with a separate FastAPI app unless you want to (see advanced option below).

```python
# ... (rest of your script unchanged)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting MCP Server")
    print("=" * 60)
    print("📡 SSE Endpoint: http://127.0.0.1:8001/sse")  # Change to your port
    print("🔍 MCP Inspector: Use http://127.0.0.1:8001/sse")
    print("⚠️  Note: http://127.0.0.1:8001 (without /sse) will give 404")
    print("=" * 60)
    # ... (rest of prints)

    mcp.run(transport="sse", port=8001)  # Add port=8001 if supported; otherwise omit and use default 8000
```

- Run the script: `python your_script.py`
- This starts the SSE server at `http://localhost:8001/sse` (adjust port as needed).

### Step 2: Update NGINX Config
Edit `/etc/nginx/sites-available/project-1-04.eduhk.hk` (use `sudo nano` or similar). Add a new `location /mcp` block inside the `server { listen 443 ssl; ... }` section. This proxies `/mcp` to the backend's `/sse`.

```nginx
server {
    listen 80;
    server_name project-1-04.eduhk.hk;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name project-1-04.eduhk.hk;
    ssl_certificate /etc/nginx/ssl/dept-wildcard.eduhk/fullchain.crt;
    ssl_certificate_key /etc/nginx/ssl/dept-wildcard.eduhk/dept-wildcard.eduhk.hk.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    ssl_trusted_certificate /etc/nginx/ssl/dept-wildcard.eduhk/fullchain.crt;
    client_max_body_size 100M;

    # Existing location
    location /langgraphplayground/ {
        proxy_pass http://localhost:2024;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # New location for MCP (proxies /mcp to backend /sse)
    location /mcp {
        proxy_pass http://localhost:8001/sse;  # Change 8001 to your MCP port
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;  # Adjust if SSE streams are long
        proxy_connect_timeout 75s;
    }

    # Existing root location
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- **Explanation**:
  - `proxy_pass http://localhost:8001/sse;`: Forwards requests to `https://project-1-04.eduhk.hk/mcp` as `/sse` on the backend (the MCP server's endpoint).
  - SSE-specific: `proxy_buffering off;` prevents NGINX from buffering the stream. The upgrade/connection headers handle any potential upgrades (though SSE is typically HTTP/1.1 chunked).
  - Timeouts: Set high to avoid dropping long-lived SSE connections.
  - If your MCP server runs on port 8000, change to `http://localhost:8000/sse`.

- Validate and reload NGINX:
  ```
  sudo nginx -t  # Check for syntax errors
  sudo systemctl reload nginx  # Or sudo nginx -s reload
  ```

### Step 3: Testing
- Access the MCP SSE endpoint via NGINX: `https://project-1-04.eduhk.hk/mcp`
- For the MCP Inspector: Connect to `https://project-1-04.eduhk.hk/mcp` (it should stream SSE data).
- Direct backend test: `curl http://localhost:8001/sse` (should show SSE stream).
- If 404 on root backend (`http://localhost:8001/`), that's expected as per your script.
- Monitor logs: `sudo tail -f /var/log/nginx/access.log` and `/var/log/nginx/error.log` for issues.

### Advanced: Integrate with FastAPI (If Needed)
If you want to run everything under one FastAPI app (e.g., on port 8001), and FastMCP exposes an ASGI app (check docs for `mcp.app` or similar), create a wrapper:

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP  # Assuming your imports

app = FastAPI()

mcp = FastMCP("mtr_next_train")
# ... (add your tools, resources, prompts as in the script)

# Mount MCP as sub-app under /mcp (if FastMCP supports it)
# Assuming mcp.get_asgi_app() exists; replace with actual method if available
app.mount("/mcp", mcp.get_asgi_app())  # Or mcp.app if exposed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

- Then update NGINX `proxy_pass http://localhost:8001/mcp/sse;` (adjust for sub-path).
- If FastMCP doesn't support mounting, stick with the standalone proxy approach.

### Potential Issues
- **Port conflicts**: Ensure port 8001 (or whatever) is free.
- **SSE compatibility**: If streaming fails, add `proxy_set_header Accept text/event-stream;` to the location.
- **SSL/HTTPS**: NGINX handles it; backend can stay HTTP.
- **Firewall**: Ensure local ports are open (e.g., ufw allow 8001).
- If errors occur, check FastMCP docs for custom path/port options.

This setup keeps your existing services (/langgraphplayground/ and /) intact.