# JSONPlaceholder API Test Automation

Automated API test suite for the public [JSONPlaceholder](https://jsonplaceholder.typicode.com) API.

## Overview

The suite covers all six JSONPlaceholder resources (`/posts`, `/comments`, `/albums`, `/photos`, `/todos`, `/users`), organized **one file per resource** (`tests/test_posts.py`, `tests/test_comments.py`, etc.) rather than one file per test type — each file holds that resource's positive CRUD cases, its negative/edge cases, and its nested-route cases together, so it reads top-to-bottom as the complete story for that resource. Values that differ between resources (ids, payloads, expected schema fields, record counts) live in one config table (`tests/resources.py`) so they aren't hardcoded repeatedly across files.

## Assumptions

- JSONPlaceholder does not persist writes; POST/PUT/PATCH/DELETE assertions check the _echoed response_, not actual state changes on a subsequent GET.
- Resource `total_count` values (100 posts, 500 comments, 100 albums, 5000 photos, 200 todos, 10 users) are fixed static values on the public instance and are asserted directly rather than fetched dynamically, to keep tests simple and fast.
- Tests run against the live public API (no local mock/stub), so they require network access and are subject to that service's availability/rate limits.
- `id: 999` was used as a "doesn't exist" id and `id: 999999` as an "out of range" id for negative tests — both fall safely outside every resource's real id range.

## Project Structure

```
.
├── requirements.txt
├── pytest.ini
├── tests/
│   ├── conftest.py       # shared fixtures (requests session, base_url)
│   ├── resources.py      # per-resource config table (ids, payloads, schemas)
│   ├── test_posts.py     # positive + negative + nested (-> /comments); also 2 misc API-wide checks
│   ├── test_comments.py  # positive + negative (leaf resource)
│   ├── test_albums.py    # positive + negative + nested (-> /photos)
│   ├── test_photos.py    # positive + negative (leaf resource)
│   ├── test_todos.py     # positive + negative (leaf resource)
│   └── test_users.py     # positive + negative + nested (-> /posts, /albums, /todos)
└── README.md
```

Each resource file follows the same internal shape: a `# ---- Positive ----` block (list, get-by-id, filter, create, replace, patch, delete), a `# ---- Negative ----` block, and — for the four resources that are parents in the graph — a `# ---- Nested ----` block.

## Execution Instructions

**1. Install dependencies** (Python 3.9+):

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Run the test suite:**

```bash
pytest tests/
```

**3. Generate an HTML report:**

```bash
pytest tests/ --html=report.html --self-contained-html
```

Open `report.html` in a browser to view results.

**4. Run a subset by marker** (`smoke`, `positive`, `negative`, `nested` — every test carries exactly one of `positive`/`negative`/`nested`, plus `smoke` on top for the fastest list/get-by-id checks):

```bash
pytest tests/ -m smoke
pytest tests/ -m positive
pytest tests/ -m negative
pytest tests/ -m nested
```

## Coverage Summary

**Routes/resources tested:** `/posts`, `/comments`, `/albums`, `/photos`, `/todos`, `/users`, plus nested routes `/posts/{id}/comments`, `/albums/{id}/photos`, `/users/{id}/posts`, `/users/{id}/albums`, `/users/{id}/todos`.

**Validations implemented:**

- Status codes for GET (list + by id), POST, PUT, PATCH, DELETE across all 6 resources
- Get-by-id tests assert an **exact match** against the real, known record for that resource's `valid_id` (`expected_record` in `resources.py`) — not just field presence/type, but the actual returned values, including nested `address`/`geo`/`company` on `/users`
- Every item returned by a list/filter endpoint (where there's no single known record to match exactly) is checked for required-field presence instead, against the field set on that resource's `expected_record` (`assert_matches_schema` in `resources.py`)
- Duplicate-id check across each resource's full list response
- Query-param filtering (`?userId=`, `?postId=`, `?albumId=`, `?username=`) and empty-result handling
- Nested-route responses cross-checked for consistency against the equivalent top-level filter (e.g. `/posts/1/comments` vs `/comments?postId=1`)
- Nested object structure validation (`address`, `address.geo`, `company` on `/users`)
- Negative cases: out-of-range id, non-numeric id, zero id, unknown resource path, empty POST body
- Two documented fake-backend quirks worth flagging in review: (1) `PUT` to a nonexistent id returns `500`, while `PATCH`/`DELETE` to the same id return `200` (fake success); (2) a path shaped like a nested route but not a real relation (e.g. `/comments/{id}/posts`) doesn't 404 — it silently returns the full, unfiltered target collection, ignoring the parent id entirely — both real, verified behavior of this API instance

**Intentionally omitted due to the 2-hour time-box:**

- Response-time/performance assertions (SLA-style checks)
- Full JSON-schema validation library (jsonschema) — used direct key/type assertions instead to save setup time
- Pagination params (`_page`, `_limit`, `_sort`) — JSONPlaceholder supports these but they weren't in the core resource list
- CI pipeline config (e.g. GitHub Actions) to auto-run the suite on push
- Contract/consumer-driven testing, load testing, or auth-related tests (API has no auth)
- Deeper negative-input fuzzing (malformed JSON bodies, wrong `Content-Type`, oversized payloads)
