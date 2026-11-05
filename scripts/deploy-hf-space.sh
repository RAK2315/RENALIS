#!/usr/bin/env bash
# Package backend/ into a standalone Docker build and push it to a Hugging Face Space.
#
# One-time setup on huggingface.co:
#   1. New Space -> Docker SDK -> any name (e.g. renalis-api) -> create.
#   2. Copy the Space's git URL, e.g. https://huggingface.co/spaces/<you>/renalis-api
#   3. Log in once with `hf auth login` using a token with write scope.
#
# Usage:
#   scripts/deploy-hf-space.sh https://huggingface.co/spaces/<you>/renalis-api
set -euo pipefail

REMOTE_URL="${1:?Usage: scripts/deploy-hf-space.sh <huggingface-space-git-url>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$(mktemp -d)"

cp -r "$ROOT/backend" "$BUILD_DIR/backend"
find "$BUILD_DIR/backend" -name "__pycache__" -type d -prune -exec rm -rf {} +
cp "$ROOT/requirements-lock.txt" "$BUILD_DIR/requirements-lock.txt"
cp "$ROOT/deploy/Dockerfile.hf" "$BUILD_DIR/Dockerfile"
cp "$ROOT/deploy/README.hf.md" "$BUILD_DIR/README.md"
cp "$ROOT/LICENSE" "$BUILD_DIR/LICENSE"

# The API also serves reports and test results that live outside backend/.
# Without these, Step 6 says "report isn't loaded" and the document links 404.
cp -r "$ROOT/docs" "$BUILD_DIR/docs"
mkdir -p "$BUILD_DIR/public" "$BUILD_DIR/data/models"
cp "$ROOT/public/renalis-architecture.svg" "$BUILD_DIR/public/"
cp "$ROOT/data/models/hemo_metrics.json" "$BUILD_DIR/data/models/"
# Copy every output/ file listed in PROJECT_DOCUMENTS. Hugging Face rejects
# plain git files over 10 MB, so larger ones are skipped with a warning.
grep -o "'output/[^']*'" "$ROOT/backend/app.py" | tr -d "'" | while read -r rel; do
  [ -f "$ROOT/$rel" ] || continue
  if [ "$(wc -c < "$ROOT/$rel")" -gt 9500000 ]; then echo "Skipping $rel (over 10 MB)"; continue; fi
  mkdir -p "$BUILD_DIR/$(dirname "$rel")"
  cp "$ROOT/$rel" "$BUILD_DIR/$rel"
done

# hf upload (not git push) because the Space rejects binary files sent over plain git.
REPO_ID="${REMOTE_URL#*huggingface.co/spaces/}"
# Call upload_folder directly: `hf upload` first tries to create the repo, which
# Hugging Face refuses (402) for Docker Spaces on free accounts even when it exists.
python -c "import sys;from huggingface_hub import HfApi;HfApi().upload_folder(repo_id=sys.argv[1],folder_path=sys.argv[2],repo_type='space',delete_patterns=['*'],commit_message='Deploy RENALIS backend')" "$REPO_ID" "$BUILD_DIR"

echo
echo "Uploaded to $REMOTE_URL"
echo "Hugging Face will build the Docker image now; watch progress on the Space's \"Logs\" tab."
echo "Build directory was $BUILD_DIR (safe to delete)."
