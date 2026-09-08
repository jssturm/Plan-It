#!/bin/bash
# Behavior test for block-dangerous-git.sh. Run: bash .cursor/hooks/test-block-dangerous-git.sh
# Cases are written as data so the dangerous strings live in a file, never in a
# shell command line that the gate itself would inspect.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
HOOK=.cursor/hooks/block-dangerous-git.sh

pass=0; fail=0
# Payloads are built with a real JSON serializer. Building them with sed made a
# test case containing && silently mangle itself (& is the whole-match reference
# in a sed replacement), which showed up as a phantom hook failure.
payload() { node -e 'process.stdout.write(JSON.stringify({command:process.argv[1],cwd:"/tmp"}))' "$1"; }

check() {
  local expected="$1" cmd="$2"
  local out
  out=$(payload "$cmd" | bash "$HOOK")
  local got
  got=$(printf '%s' "$out" | sed -n 's/.*"permission"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p')
  if [ "$got" = "$expected" ]; then
    pass=$((pass + 1)); printf 'PASS  %-6s %s\n' "$got" "$cmd"
  else
    fail=$((fail + 1)); printf 'FAIL  want=%-5s got=%-5s %s\n' "$expected" "$got" "$cmd"
  fi
}

# Destructive git invocations must be denied.
check deny  'git reset --hard HEAD~1'
check deny  'git clean -fd'
check deny  'git clean -f'
check deny  'git branch -D feature'
check deny  'git checkout .'
check deny  'git restore .'
check deny  'git push --force origin main'
check deny  'cd repo && git reset --hard'

# Publishing needs a human.
check ask   'git push origin main'
check ask   'git push --force-with-lease origin main'
check ask   'git -C Plan-It push'

# Ordinary work is untouched.
check allow 'git status'
check allow 'git diff main'
check allow 'git -C Plan-It diff main'
check allow 'git commit -m fix'
check allow 'git checkout main'
check allow 'git restore --staged file.txt'
check allow 'npm run build'

# The strings appearing inside another program's arguments are not git commands.
check allow 'rg -n "git reset --hard" docs/'
check allow 'echo see the git push policy'

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
