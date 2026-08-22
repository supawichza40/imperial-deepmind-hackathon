# ADR-007 — Two-pass span merge algorithm

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** the single-pass merge in the original design draft

## Context
The original merge algorithm iterated sorted spans and compared each to the "previous kept span". This was not transitive: a span B overlapping span A, and span C overlapping B but not A, would be orphaned once B was marked "used". Result: overlapping spans could survive into the sanitiser, corrupting the redacted output.

Both reviewers flagged this in round 2.

## Decision
**Two-pass algorithm:**
1. **Pass 1 (same-type merge):** group by type, sort by start, merge overlapping spans within each group. Collect merged-per-type spans.
2. **Pass 2 (cross-type resolution):** sort all merged spans by (start asc, end desc), iterate sequentially, compare each against the last span in the result list. If overlapping and different type, keep the longer one.

## Consequences
- No orphaned spans — all overlaps are resolved globally.
- Pass 2 is safe because sorting by start ascending guarantees that replacing `result[-1]` with a longer span can never create an overlap with `result[-2]`.
- The worked example in the design doc traces through a concrete case.

## Related
- [Design §3.3](../specs/design.md)
- [ADR-002 (merge rule)](002-span-merge-and-reverse-replacement.md)