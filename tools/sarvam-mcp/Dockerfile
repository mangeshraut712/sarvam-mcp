FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

RUN pip install --no-cache-dir .

ENV SARVAM_MCP_TRANSPORT=http
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["sarvam-mcp-http"]
