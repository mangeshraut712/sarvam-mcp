"""Shared types + helpers used across tool modules.

Keeps language enums, speaker enums, and tool-context lookup in one place
so tool modules can stay short and focused on their endpoint shape.
"""

from __future__ import annotations

from typing import Literal

from fastmcp import Context

from sarvam_mcp._registry import ServerContext

# ---- Language codes -------------------------------------------------------
#
# Sarvam uses BCP-47-style codes with the ISO 639-3 language subtag for
# constitutionally-listed languages. ``unknown`` lets the API auto-detect.

LanguageCode = Literal[
    "en-IN",  # English
    "hi-IN",  # Hindi
    "bn-IN",  # Bengali
    "ta-IN",  # Tamil
    "te-IN",  # Telugu
    "gu-IN",  # Gujarati
    "kn-IN",  # Kannada
    "ml-IN",  # Malayalam
    "mr-IN",  # Marathi
    "pa-IN",  # Punjabi
    "od-IN",  # Odia
    "as-IN",  # Assamese
    "ur-IN",  # Urdu
    "ne-IN",  # Nepali
    "kok-IN",  # Konkani
    "ks-IN",  # Kashmiri
    "sd-IN",  # Sindhi
    "sa-IN",  # Sanskrit
    "sat-IN",  # Santali
    "mni-IN",  # Manipuri
    "brx-IN",  # Bodo
    "mai-IN",  # Maithili
    "doi-IN",  # Dogri
    "unknown",  # Auto-detect
]

# Subset that Bulbul v3 (TTS) supports. STT covers all 23 above.
TtsLanguageCode = Literal[
    "en-IN",
    "hi-IN",
    "bn-IN",
    "ta-IN",
    "te-IN",
    "gu-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "pa-IN",
    "od-IN",
]


# ---- Bulbul speakers ------------------------------------------------------
#
# Live-tested 2026-04-27. Full speaker rosters per model variant.
#
# Bulbul v3 is the latest and is the default `model` everywhere; v2 speakers
# are accepted by `bulbul:v2` only. We expose the union as a Literal so MCP
# clients can autocomplete, and let the API do model-vs-speaker compatibility
# checks at request time (with a helpful error if mismatched).

BulbulSpeaker = Literal[
    # --- Bulbul v3 roster (38 speakers, the modern set) --------------------
    "aditya", "ritu", "ashutosh", "priya", "neha", "rahul", "pooja", "rohan",
    "simran", "kavya", "amit", "dev", "ishita", "shreya", "ratan", "varun",
    "manan", "sumit", "roopa", "kabir", "aayan", "shubh", "advait", "anand",
    "tanya", "tarun", "sunny", "mani", "gokul", "vijay", "shruti", "suhani",
    "mohit", "kavitha", "rehan", "soham", "rupali", "niharika",
    # --- Bulbul v2-only legacy speakers ------------------------------------
    "anushka", "abhilash", "manisha", "vidya", "arya", "karun", "hitesh",
]


# ---- Translate-mode + script enums ---------------------------------------

TranslateMode = Literal["formal", "modern-colloquial", "classic-colloquial", "code-mixed"]
OutputScript = Literal["roman", "fully-native", "spoken-form-in-native"]
NumeralsFormat = Literal["international", "native"]
SpeakerGender = Literal["Male", "Female"]


# ---- Server context lookup -----------------------------------------------


def server_ctx(ctx: Context) -> ServerContext:
    """Pull the lifespan-managed ServerContext off a tool ``Context``.

    Sync — does NOT verify auth. Use ``await ready_ctx(ctx)`` from any tool
    function that needs to make API calls.
    """
    lifespan = ctx.request_context.lifespan_context
    if not isinstance(lifespan, ServerContext):
        raise RuntimeError(
            "Lifespan context is not a ServerContext — server.py wiring is broken."
        )
    return lifespan


async def ready_ctx(ctx: Context) -> ServerContext:
    """Pull the ServerContext + ensure auth is set (eliciting from the client
    if necessary). Every tool that calls the Sarvam API should ``await`` this
    on its first line.
    """
    from sarvam_mcp.auth.elicit import ensure_auth  # lazy to avoid circular import

    await ensure_auth(ctx)
    return server_ctx(ctx)
