#!/usr/bin/env bash
# Keep the `skills-only` orphan branch in sync with the tutorial repo.
#
# `npx skills add luochang212/dive-into-langgraph` clones `skills-only` instead
# of `main`, because the skill is a small fraction of this repo (no notebooks,
# no app, no docs build). The branch therefore has to be refreshed by hand
# whenever the skill changes — this script is that refresh.
#
# Usage:
#   scripts/sync_skills_branch.sh              # export, commit, push
#   scripts/sync_skills_branch.sh --check      # exit 1 when the branch is stale
#   scripts/sync_skills_branch.sh --no-push    # commit in a kept worktree only
#   scripts/sync_skills_branch.sh --no-fetch   # trust the local origin ref (offline)
#   scripts/sync_skills_branch.sh --ref <rev>  # export from something else than main
#
# Requires: git, tar.

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

REF=main
BRANCH=skills-only
CHECK=0
PUSH=1
FETCH=1

# Paths mirrored onto the branch. Everything else on main stays behind — in
# particular the rest of img/ (ebook screenshots) must not follow, the branch
# stays small on purpose.
PATHS=(skills/dive-into-langgraph README.md .gitignore img/social-preview.webp)

usage() {
  sed -n '2,/^$/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1 ;;
    --no-push) PUSH=0 ;;
    --no-fetch) FETCH=0 ;;
    --ref) REF=${2:?--ref needs a revision}; shift ;;
    --branch) BRANCH=${2:?--branch needs a name}; shift ;;
    -h | --help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

git rev-parse --verify --quiet "$REF^{commit}" >/dev/null || {
  echo "error: no such revision: $REF" >&2
  exit 2
}

fetch_remote() {
  # GitHub over HTTP/2 occasionally fails with "Error in the HTTP2 framing
  # layer"; retrying over HTTP/1.1 is the known workaround.
  local attempt
  for attempt in 1 2 3; do
    if git -c http.version=HTTP/1.1 fetch --quiet origin "$BRANCH" 2>/dev/null; then
      return 0
    fi
    sleep 2
  done
  return 1
}

if [ "$FETCH" = 1 ]; then
  if ! fetch_remote; then
    echo "error: cannot fetch origin/$BRANCH (offline? try --no-fetch)" >&2
    exit 2
  fi
fi

if ! git rev-parse --verify --quiet "refs/remotes/origin/$BRANCH^{commit}" >/dev/null; then
  echo "error: origin/$BRANCH not found — fetch it (or drop --no-fetch)" >&2
  exit 2
fi

if [ "$CHECK" = 1 ]; then
  # The branch must be *exactly* the projection of PATHS, so compare file lists
  # too: content diff alone would miss a stray file left on the branch.
  expected=$(git ls-tree -r --name-only "$REF" -- "${PATHS[@]}" | sort)
  actual=$(git ls-tree -r --name-only "origin/$BRANCH" | sort)
  names=$(diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") || true)
  content=$(git diff --name-status "$REF" "origin/$BRANCH" -- "${PATHS[@]}" || true)
  if [ -n "$names" ] || [ -n "$content" ]; then
    echo "origin/$BRANCH has drifted from $REF:" >&2
    if [ -n "$names" ]; then
      echo "-- files only on one side --" >&2
      printf '%s\n' "$names" >&2
    fi
    if [ -n "$content" ]; then
      echo "-- differing content --" >&2
      printf '%s\n' "$content" >&2
    fi
    echo "" >&2
    echo "run scripts/sync_skills_branch.sh to refresh it" >&2
    exit 1
  fi
  echo "origin/$BRANCH is in sync with $REF"
  exit 0
fi

TMP=$(mktemp -d)
cleanup() {
  git worktree remove --force "$TMP/branch" >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap cleanup EXIT

git worktree add --quiet --detach "$TMP/branch" "origin/$BRANCH"

# Rebuild the worktree from scratch instead of layering files on top: anything
# the branch carries outside PATHS is drift too, and dropping everything first
# is the only way to be sure it goes away. `git archive` also keeps untracked
# junk in the working tree (.DS_Store, __pycache__) off the branch.
cd "$TMP/branch"
git rm -r -q --cached --ignore-unmatch . >/dev/null 2>&1 || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
git -C "$ROOT" archive "$REF" -- "${PATHS[@]}" | tar -x -C .

git add -A
if git diff --cached --quiet; then
  echo "origin/$BRANCH already matches $REF; nothing to commit"
  exit 0
fi

# --no-verify: the throwaway worktree of an orphan branch has no
# .pre-commit-config.yaml, so the shared hook would refuse the commit. The
# content is exported verbatim from $REF, which pre-commit already gated there.
SYNCED_FROM=$(git -C "$ROOT" rev-parse --short "$REF")
git commit --no-verify --quiet -m "chore(skills-only): sync skill from $REF@$SYNCED_FROM"
echo "committed $(git rev-parse --short HEAD) on top of origin/$BRANCH"
git --no-pager diff --stat "origin/$BRANCH" HEAD

if [ "$PUSH" = 0 ]; then
  trap - EXIT
  echo ""
  echo "left in $TMP/branch (detached HEAD) — inspect, then push with:"
  echo "  git -C $TMP/branch push origin HEAD:refs/heads/$BRANCH"
  exit 0
fi

for attempt in 1 2 3; do
  if git -c http.version=HTTP/1.1 push origin "HEAD:refs/heads/$BRANCH"; then
    echo "pushed to origin/$BRANCH"
    exit 0
  fi
  sleep 2
done

echo "error: push failed; the commit is at $(git rev-parse --short HEAD) in $TMP/branch" >&2
trap - EXIT
exit 1
