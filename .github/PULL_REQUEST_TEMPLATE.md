## Summary

<!-- What changed and why. -->

## Checklist

- [ ] `pytest -q` passes
- [ ] `ruff check .` passes
- [ ] If `web/` changed: `cd web && npx tsc --noEmit`
- [ ] No API keys or `.env` files committed
- [ ] New WebMCP tools use `registerTool` + `AbortSignal` and update shared UI state
