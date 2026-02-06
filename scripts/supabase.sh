#!/usr/bin/env bash
# Start or stop local Supabase. Run from repo root or any directory.
# Usage: ./scripts/supabase.sh start | stop | status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

cmd="${1:-}"

case "$cmd" in
  start)
    echo "Starting Supabase (project root: $REPO_ROOT)..."
    npx supabase start
    echo ""
    echo "Supabase is up. Studio: http://127.0.0.1:54323 — run './scripts/supabase.sh status' to see credentials again."
    ;;
  stop)
    echo "Stopping Supabase..."
    npx supabase stop
    echo "Supabase stopped. Data is preserved."
    ;;
  status)
    npx supabase status
    ;;
  *)
    echo "Usage: $0 start | stop | status" >&2
    echo "" >&2
    echo "  start   — start local Supabase (Docker must be running)" >&2
    echo "  stop    — stop Supabase (keeps data)" >&2
    echo "  status  — show URLs and keys" >&2
    exit 1
    ;;
esac
