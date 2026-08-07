#!/usr/bin/env bash
# Creates (or updates) a gh-pages branch from the built site/ directory.
# Usage: ./scripts/deploy_gh_pages.sh [--push]
#   --push  also push the gh-pages branch to origin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PUSH=false
if [[ "${1:-}" == "--push" ]]; then
  PUSH=true
fi

SRC_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "==> Building site..."
python3 scripts/build_aec.py

echo "==> Staging built artifacts..."
TMPDIR_GH="$(mktemp -d)"
cp -r site/* "$TMPDIR_GH/"

echo "==> Creating/refresing gh-pages branch..."

# Remove site/ from the working tree before switching so git checkout
# does not choke on modified generated files tracked on the source branch.
rm -rf site/

if git rev-parse --verify gh-pages >/dev/null 2>&1; then
  git checkout --force gh-pages
else
  git checkout --orphan gh-pages
fi

# Wipe everything from the index and working tree (including dotfiles)
git rm -r --cached . >/dev/null 2>&1 || true
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# Drop the built site at the root
cp -r "$TMPDIR_GH"/* .

# Stub README so the branch has documentation
cat > README.md <<'EOF'
# KhulnaSoft Engineering Knowledge OS — gh-pages

Static build of the Engineering Knowledge OS portal, generated from
the `init` branch by `scripts/deploy_gh_pages.sh` (python3 scripts/build_aec.py).
Do not edit files on this branch directly.
EOF

git add -A
git commit -m "Deploy site (from ${SRC_BRANCH})" --allow-empty

rm -rf "$TMPDIR_GH"

if $PUSH; then
  echo "==> Pushing gh-pages to origin..."
  git push origin gh-pages:gh-pages --force-with-lease
fi

git checkout "$SRC_BRANCH"

echo "==> gh-pages branch is up to date with built site."
if $PUSH; then
  echo "==> gh-pages pushed to origin."
else
  echo "==> Run with --push to publish."
fi
