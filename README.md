Project: Pointr Assignment

Overview
- REST API using FastAPI + SQLModel (SQLite) with pytest-based API tests
- UI automation using Selenium (Chrome and Firefox) with pytest
- CI/CD via GitHub Actions to run API and UI tests headlessly and upload artifacts

Prerequisites
- Python 3.10+
- Google Chrome and Mozilla Firefox installed (for local UI tests)
- Drivers are auto-managed by webdriver-manager; no manual install required

Setup
1) Create and activate a venv
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

2) Install dependencies
   pip install -r requirements.txt

Question #1 - REST

Run API locally
- Start server (choose one):
  - Direct: uvicorn app.main:app --reload
  - Helper script: ./run.sh  # or: ./run.sh 0.0.0.0 8000
- Interactive docs (OpenAPI):
  http://127.0.0.1:8000/docs
- Root endpoint now returns a helpful message instead of 404:
  http://127.0.0.1:8000/

Implemented endpoints
- Site
  - POST /sites        -> import a new site
  - GET  /sites/{id}   -> retrieve an existing site
  - DELETE /sites/{id} -> delete a site
- Building
  - POST /buildings        -> import a building
  - GET  /buildings/{id}   -> retrieve a building
  - DELETE /buildings/{id} -> delete a building
- Levels
  - POST /levels -> import a single Level object or a list of Level objects

Example requests (curl)
- Create a site
  curl -s -X POST http://127.0.0.1:8000/sites \
       -H 'Content-Type: application/json' \
       -d '{"name":"Hospital","description":"Main campus"}'

- Get a site
  curl -s http://127.0.0.1:8000/sites/1

- Delete a site
  curl -i -X DELETE http://127.0.0.1:8000/sites/1

- Create a building for a site (replace SITE_ID)
  curl -s -X POST http://127.0.0.1:8000/buildings \
       -H 'Content-Type: application/json' \
       -d '{"name":"Block A","site_id":SITE_ID}'

- Import multiple levels (replace BUILDING_ID)
  curl -s -X POST http://127.0.0.1:8000/levels \
       -H 'Content-Type: application/json' \
       -d '[{"name":"Ground","number":0,"building_id":BUILDING_ID},{"name":"First","number":1,"building_id":BUILDING_ID}]'

Run API tests
- Tests use an in-memory SQLite database configured per test and run via pytest.
  pytest tests/api -q

Question #2 - UI

Goal
- Validate the Pointr blog works as expected and compute the top words from recent posts.

What the UI automation does (simple overview)
- Opens https://www.pointr.tech/blog
- Checks that article content appears (cards or article links)
- Visits the latest 3 articles, extracts text, computes the 5 most repeated words (counting all words), and saves them to artifacts/top_words.txt
- Runs on at least two browsers: Chrome and Firefox

How to run UI tests locally
1) Prerequisites: Chrome installed. Firefox is optional (if not installed, Firefox cases are skipped automatically).
2) Run all UI tests:
   pytest tests/ui -q
3) See the result file:
   cat artifacts/top_words.txt
   (Each line looks like: word: count)

Notes
- Tests run headless and download drivers automatically using webdriver-manager.
- If Chrome fails due to sandboxing, try: CHROME_ARGS="--no-sandbox --disable-dev-shm-usage" (not usually needed).

CI/CD
- Workflow: .github/workflows/ci.yml
  - Installs dependencies
  - Runs API tests first
  - Sets up Chrome and Firefox, then runs UI tests headlessly on both
  - Uploads artifacts/top_words.txt as a build artifact

Implementation pointers
- Browser fixture: tests/ui/conftest.py (well‑documented helpers make Chrome/Firefox setup straightforward)
- Test logic: tests/ui/test_blog_top_words.py (small helper functions for clarity: link discovery, page text scraping, tokenizing, and saving results)

Project structure
- app/
  - main.py (FastAPI app and endpoints)
  - models.py (SQLModel models)
  - db.py (DB engine/session helpers)
- tests/
  - api/ (pytest API tests)
  - ui/ (Selenium tests for Chrome and Firefox)
- .github/workflows/ci.yml (CI pipeline)

Additional notes
- Default local database is SQLite file pointr.db. Tests use a shared in-memory DB.
- Buildings optionally reference a Site; Levels optionally reference a Building. Input validation ensures referenced entities exist.
- /levels accepts either a single object or an array for bulk import.
