# Design Decisions

## 2026-09-29 — /ask accepts a list of questions
**Context:** The spec says "ask a question", but the original goal was answering a list.
**Decision:** The request has `questions: list[str]` (1–20 items); the response has one result per question, in the same order.
**Why:** Covers both cases — a single question is a list of one. The 20-item cap limits cost and abuse.
**Trade-off:** Questions should be answered concurrently, and one failing question must not fail the whole request.

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

## 2026-10-06 — PostgreSQL + pgvector in Docker
**Context:** Chunks need to be stored with their text, metadata (document, page/row) and embeddings, and searched by similarity.
**Decision:** Use PostgreSQL 17 with the pgvector extension (`pgvector/pgvector:pg17` image), run via Docker Compose with a named volume (`pgdata`).
**Why:** One database holds both normal data and vectors — no separate vector database to run. Docker makes it reproducible; the volume keeps data across container restarts.
**Trade-off:** Dev credentials are written in docker-compose.yml for now — acceptable only for local development

## 2026-10-06 — requirements.txt lives in backend/
**Decision:** The dependency list is `backend/requirements.txt`; run `pip freeze` from `backend/`.
**Why:** The API's Dockerfile will live in backend/, next to its dependency list.

## 2026-10-10 — CSV row numbers follow Excel: 
**Decision:** Rows start from index 2, the header is row 1
**Why:** To allow a person to open the file and find the cited row. 

## 2026-10-10 - Chunks are split by tokens, not characters:
**Context** A first attempt split pages at 700 characters, but 11 chunks were still over the embedding model's 256-token limit, turns out
it was because the PDF includes Chinese pages, where one character is about one token.
**Decision** Content is split using a 200-token limit, measured with the embedding model’s own tokenizer. 256 is the limit, but the 
split limit was set to 200 to leave a safety margin
**Why:** the model ignores everything past 256 tokens, and a character count was wrong for the Chinese pages, so 11 chunks went over the limit, 
and any text over the limit is ignored.

## 2026-10-10 - A whole-table chunk for the CSV, on top of the row chunks:
**Decision:** Append an extra entry which contains all the rows of the table as one chunk 
**Why:** Counting questions (like PWM pins) need all rows together. 
**Trade-off:** its vector reflects only the first 256 tokens, though Claude still receives the full text.

## 2026-10-10 - Chinese pages (19–34) kept for now: 
**Context:** Pages 19 to 34, and the table of contents on page 4, are a Chinese translation of the English pages.
**Decision:** Keep all pages for now.
**Why:** It's the simplest starting point.
**Trade-off:** They duplicate the English content, and the embedding model is English-only, so they may add noise. If they do, they will be removed

## 2026-10-10 - Re-uploading a file replaces its old rows (delete and insert in one transaction): 
**Decision:** Delete the document's old rows and insert the new ones in a single transaction.
**Why:** Avoids duplicates, and a failed upload can't lose the old data.

## 2026-10-12 - Embedding runs inside the upload request
**Decision:** Run the embedding step directly in the request.
**Why:** Simpler and fine for a demo.
**Trade-off:** The server is blocked while it runs, so a large PDF freezes other requests for a few seconds. A possible fix is to run it in a background thread.

## 2026-10-12 - Upload accepts only .pdf and .csv, checked by file ending
**Decision:** Check the file ending, case-insensitive. Anything else gets a 400 error.
**Why:** Simple and fine for a demo.
**Trade-off:** A filename can lie. A stricter check would confirm that a PDF starts with `%PDF-`.

## 2026-10-18 Chunk size stays at 200 tokens
**Decision:** Kept MAX_TOKENS = 200 after testing 100.
**Why:** At 100 tokens, Q2 (output voltage) still missed and other questions that had hit started to miss.
**Trade-off:** Q2 stays a known miss for pure vector search: the +3V3/+5V rows sit inside a pin-table chunk whose overall meaning is "analog pins". Planned fix: hybrid search (vector + keyword).

## 2026-10-18 Test expectation corrections
**Decision:** Fixed expected pages of results
**Why:** The results' expected pages were incorrect, leading to a constant misses

## 2026-10-19 Fixed format of results and made it clear 
**Decision:** Sources are numbered, and Claude cites by number. 
**Why:** our code maps numbers back to document/page/row, so Claude can’t invent a citation.