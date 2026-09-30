# Design Decisions

## 2026-09-29 — /ask accepts a list of questions
**Context:** The spec says "ask a question", but the original goal was answering a list.
**Decision:** The request has `questions: list[str]` (1–20 items); the response has one result per question, in the same order.
**Why:** Covers both cases — a single question is a list of one. The 20-item cap limits cost and abuse.
**Consequences:** Questions should be answered concurrently, and one failing question must not fail the whole request.

## 2026-09-29 — Separate `answerable` boolean in each result
**Context:** The spec requires answering "not enough information" when documents don't contain the answer.
**Decision:** Each result has `answerable: bool` alongside the text answer.
**Why:** Code (like the evaluation script) can check a boolean reliably; checking the wording of a sentence is fragile.

## 2026-09-29 — Citations store document + page or row
**Context:** The spec requires citations to the exact document and page (PDF) or row (CSV).
**Decision:** `Citation` has `document`, plus optional `page` and `row`. Every stored chunk must keep its page/row number from ingestion onward.
**Why:** Page numbers can't be recovered after extraction if they weren't saved. One model covers both file types.

## 2026-09-30 — Reject unknown fields in requests
**Context:** Pydantic silently ignores unknown fields by default.
**Decision:** Request models use `extra="forbid"`.
**Why:** A misspelled optional field would otherwise be silently ignored, producing confusing behaviour with no error.