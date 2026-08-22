# ADR-008 — Best-match offset resolution with claimed intervals

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** the sequential `search_from` pointer in design round 1

## Context
Round 1 used a monotonic `search_from` pointer that advanced past each match. This assumed Gemma returns fields in top-to-bottom document order. Gemini's review flagged that LLMs frequently return extracted fields out of order — if Gemma returns a field at character 150 first, `search_from` jumps past 150, and all preceding fields (like "A. Okafor" at ~25) return -1 and are silently dropped.

## Decision
For each Gemma item, call `text.find(item["text"])`. If the substring appears multiple times, pick the occurrence not yet claimed by a previous span. Track claimed intervals `[(start, end)]`; for each new item, find the first occurrence whose position doesn't overlap any claimed interval.

## Consequences
- Handles both out-of-order returns and repeated substrings (e.g. "Pelham" ×3 in fixtures).
- If no unclaimed occurrence is found, the span is dropped with a warning — no silent data loss.
- Slightly more complex than a monotonic pointer, but correct.

## Related
- [Design §3.3](../specs/design.md)
- [ADR-001 (Gemma returns text, not offsets)](001-gemma-returns-text-not-offsets.md)