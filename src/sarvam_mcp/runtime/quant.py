"""B3 — size math for PTQ bit-widths (not a real GPTQ/AWQ implementation)."""

from __future__ import annotations


def weight_bytes(param_count: int, bits: int) -> int:
    if bits not in {16, 8, 4, 3, 2}:
        raise ValueError("bits must be 16, 8, 4, 3, or 2")
    return (param_count * bits + 7) // 8


def size_vs_fp16(bits: int) -> float:
    return bits / 16
