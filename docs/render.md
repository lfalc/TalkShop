# Render deployment notes

Tested locally to emulate Render’s environment. Here’s what can go wrong and how to avoid it.

## Root directory (important)

**Use repo root.** In Render dashboard → Service → Settings → **Root Directory**, leave it **blank** (or `.`).

- If you set Root Directory to `src`, the build runs from `src/` and **cannot see** `requirements.txt` (it lives in the repo root; Render does not expose parent when root is set). You’d get build or start failures.
- With repo root, the start command must add `src` to the path so Python can find the `api` package: use `PYTHONPATH=src` in the start command below.

## Errors Render might see

### 1. **`ModuleNotFoundError: No module named 'api'`**

- **Cause:** Start command is run from **repo root** without `api` on the Python path, or the start command is wrong (e.g. `python -m api.main` instead of uvicorn).
- **Happens when:** Root Directory is repo root but start command is `python -m api.main` (that runs the module as a script; the app is `api.main:app` and must be run with **uvicorn**). Also if you use `uvicorn api.main:app` without `PYTHONPATH=src`.
- **Fix:** Root Directory = blank. Start command: `PYTHONPATH=src python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`.

### 2. **`ValueError: DATABASE_URL environment variable not set`**

- **Cause:** App reads `DATABASE_URL` in lifespan; Render does not deploy `.env`.
- **Fix:** In Render dashboard → Service → Environment, add `DATABASE_URL` (e.g. from Supabase connection string).

### 3. **`No module named 'click'` (or wrong uvicorn)**

- **Cause:** Shell uses a different Python (e.g. Homebrew) than the one that ran `pip install`.
- **Fix:** Use `python -m uvicorn ...` (or Render’s Python explicitly) so the same interpreter and deps are used.

### 4. **`run.py` from repo root**

- **Cause:** `python src/api/run.py` runs with cwd = repo root. Uvicorn subprocess also has cwd = repo root, so it can’t import `api`.
- **Fix:** Don’t use `run.py` as the Render start command. Use the uvicorn command below. If you keep `run.py` for local dev, use it only when cwd is `src` and you run `python -m api.run`.

### 5. **Tests failing in CI (fresh install)**

- **Cause:** Fresh `pip install -r requirements.txt` can pull **pytest 9.x**. With pytest-asyncio, “sync test depending on async fixture” becomes an error, so all tests error at fixture setup.
- **Fix:** Pin pytest in `requirements.txt` (e.g. `pytest>=7.0.0,<9`) until tests are updated to use async tests with async fixtures, or run tests only from your local/CI that already pins versions.

## Recommended Render setup

| Setting | Value |
|--------|--------|
| **Root Directory** | *(leave blank — repo root)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `PYTHONPATH=src python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| **Environment** | `DATABASE_URL` (and any others from `.env`) in the dashboard |

**Do not use:** `python -m api.main` — that does not start the web server; the app is served by uvicorn with the app object `api.main:app`.

If you use the repo’s `render.yaml` (Blueprint), the start command is already set. Ensure the service’s Root Directory is not overridden to `src`.
