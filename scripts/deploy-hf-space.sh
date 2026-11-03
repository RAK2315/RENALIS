#!/usr/bin/env bash
# Package backend/ into a standalone Docker build and push it to a Hugging Face Space.
#
# One-time setup on huggingface.co:
#   1. New Space -> Docker SDK -> any name (e.g. renalis-api) -> create.
#   2. Copy the Space's git URL, e.g. https://huggingface.co/spaces/<you>/renalis-api
#   3. Have a HF access token with write scope ready; when git prompts for a
#      password over HTTPS, paste the token (your account name as the username).
#
# Usage:
#   scripts/deploy-hf-space.sh https://huggingface.co/spaces/<you>/renalis-api
set -euo pipefail

REMOTE_URL="${1:?Usage: scripts/deploy-hf-space.sh <huggingface-space-git-url>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$(mktemp -d)"

cp -r "$ROOT/backend" "$BUILD_DIR/backend"
cp "$ROOT/requirements-lock.txt" "$BUILD_DIR/requirements-lock.txt"
cp "$ROOT/deploy/Dockerfile.hf" "$BUILD_DIR/Dockerfile"
cp "$ROOT/deploy/README.hf.md" "$BUILD_DIR/README.md"
cp "$ROOT/LICENSE" "$BUILD_DIR/LICENSE"

cd "$BUILD_DIR"
git init -q
git add -A
git -c user.email="deploy@local" -c user.name="RENALIS deploy" commit -q -m "Deploy RENALIS backend"
git branch -M main
git remote add space "$REMOTE_URL"
git push --force space main

echo
echo "Pushed to $REMOTE_URL"
echo "Hugging Face will build the Docker image now; watch progress on the Space's \"Logs\" tab."
echo "Build directory was $BUILD_DIR (safe to delete)."
