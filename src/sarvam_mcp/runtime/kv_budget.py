"""B4 / B7 — KV-cache bytes and max context for MHA / MQA / GQA."""

from __future__ import annotations

from typing import Literal

Attention = Literal["mha", "mqa", "gqa"]


def kv_heads(attention: Attention, num_heads: int, num_groups: int = 1) -> int:
    if attention == "mha":
        return num_heads
    if attention == "mqa":
        return 1
    return max(1, num_groups)


def kv_cache_bytes(
    *,
    layers: int,
    num_heads: int,
    head_dim: int,
    seq_len: int,
    attention: Attention = "gqa",
    num_groups: int = 8,
    bytes_per_elem: int = 2,
) -> int:
    heads = kv_heads(attention, num_heads, num_groups)
    # K and V
    return layers * heads * head_dim * seq_len * bytes_per_elem * 2


def max_context_tokens(
    *,
    kv_budget_bytes: int,
    layers: int,
    num_heads: int,
    head_dim: int,
    attention: Attention = "gqa",
    num_groups: int = 8,
    bytes_per_elem: int = 2,
) -> int:
    per_token = kv_cache_bytes(
        layers=layers,
        num_heads=num_heads,
        head_dim=head_dim,
        seq_len=1,
        attention=attention,
        num_groups=num_groups,
        bytes_per_elem=bytes_per_elem,
    )
    if per_token <= 0:
        return 0
    return kv_budget_bytes // per_token
