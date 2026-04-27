"""Sarvam Vision — document/image OCR with table preservation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from sarvam_mcp.observability import measure_tool
from sarvam_mcp.tools._common import LanguageCode, ready_ctx

# NOTE: As of 2026-04-27 live testing, none of the obvious paths
# (/parse, /parsedoc, /parse-doc, /parse/parsedoc, /document/parse,
#  /v1/parse, /v1/document/parse, /vision/parse, etc.) responded on
# api.sarvam.ai with the standard API key. Sarvam Vision OCR may not be
# GA on every account, may live on a separate host, or use a non-obvious
# path. Update this constant once the official endpoint is confirmed
# (likely via Sarvam internal docs or the dashboard).
PARSE_PATH = "/parse/parsedoc"

OutputFormat = Literal["markdown", "html", "json"]


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_vision_extract",
        description=(
            "Extract text + structure from a document or image using Sarvam Vision. "
            "Supports 23 Indian languages with table preservation. Outputs "
            "markdown (default), HTML, or structured JSON."
        ),
    )
    async def sarvam_vision_extract(
        ctx: Context,
        document_path: str = Field(
            description="Absolute path to a PDF or image (png/jpg/jpeg/webp).",
        ),
        output_format: OutputFormat = Field(default="markdown"),
        language_code: LanguageCode = Field(
            default="unknown",
            description="Language hint. 'unknown' lets the model auto-detect.",
        ),
        page_number: int | None = Field(
            default=None, ge=1, description="If set, parse only this 1-indexed page (PDFs)."
        ),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        path = Path(document_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Document not found: {path}")

        with measure_tool() as metrics:
            with path.open("rb") as fh:
                files = {"file": (path.name, fh, _guess_doc_mime(path))}
                data: dict[str, Any] = {
                    "output_format": output_format,
                    "language_code": language_code,
                }
                if page_number is not None:
                    data["page_number"] = str(page_number)
                payload, call = await sc.client.post_multipart(
                    PARSE_PATH, data=data, files=files
                )
            metrics.merge(call)

        return {
            "content": payload.get("content") or payload.get("output"),
            "format": output_format,
            "page_count": payload.get("page_count"),
            "language_code": payload.get("language_code"),
            "raw": payload,
            "observability": metrics.to_response_block(),
        }


def _guess_doc_mime(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "tiff": "image/tiff",
    }.get(suffix, "application/octet-stream")
