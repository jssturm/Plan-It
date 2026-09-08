#!/bin/bash
# Cursor beforeShellExecution gate for irreversible git commands.
#
# Reads the hook payload on stdin and prints a permission decision on stdout.
# Only fires on commands the matcher in .cursor/hooks.json already flagged, so
# failClosed can stay on: a broken gate blocks flagged commands only, never
# ordinary work.
#
#   deny -> destroys uncommitted or unreachable work with no undo
#   ask  -> publishes to a shared remote; a human confirms
#
# Detection is anchored to command position. The dangerous text merely appearing
# inside a quoted argument (a grep pattern, a node -e script, a doc edit) is not
# a git invocation and must not be blocked, or the gate becomes noise and gets
# switched off.
set -uo pipefail

INPUT=$(cat)

# Extraction must be a real JSON parse. A regex "good enough" extract silently
# mangles the command (a greedy match swallows the following JSON fields), and a
# mangled command fails to match the patterns below, so the gate opens without
# any error. jq is not installed on every host; node is a hard hub dependency.
if command -v jq >/dev/null 2>&1; then
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.command // empty')
elif command -v node >/dev/null 2>&1; then
  COMMAND=$(printf '%s' "$INPUT" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{process.stdout.write(String(JSON.parse(s).command||""))}catch{process.exit(1)}})')
else
  # No parser at all: refuse to guess. The matcher already flagged this command
  # as dangerous, so failing closed is the safe direction.
  printf '{"permission": "deny", "user_message": "Git guardrail cannot parse the command (no jq or node). Blocked as a precaution.", "agent_message": "The git guardrail hook has no JSON parser available, so it blocked this flagged command rather than guess."}\n'
  exit 0
fi

allow() { echo '{"permission": "allow"}'; exit 0; }
[ -z "$COMMAND" ] && allow

json_str() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/'; }

emit() {
  printf '{"permission": "%s", "user_message": %s, "agent_message": %s}\n' "$1" "$2" "$3"
  exit 0
}

DESTRUCTIVE=(
  'reset[[:space:]]+--hard'
  'clean[[:space:]]+-[a-zA-Z]*f'
  'branch[[:space:]]+-D'
  'checkout[[:space:]]+\.([[:space:]]|$)'
  'restore[[:space:]]+\.([[:space:]]|$)'
)

# Split on shell separators so each segment can be judged on its own first token.
SEGMENTS=$(printf '%s' "$COMMAND" | sed 's/&&/\n/g; s/||/\n/g; s/;/\n/g; s/|/\n/g')

while IFS= read -r seg; do
  # Strip leading whitespace, sudo, and inline VAR=value assignments.
  seg=$(printf '%s' "$seg" | sed 's/^[[:space:]]*//; s/^sudo[[:space:]]\+//; s/^\([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]\+\)*//')

  # Only a segment that actually invokes git is a git command.
  printf '%s' "$seg" | grep -qE '^git([[:space:]]|$)' || continue

  for p in "${DESTRUCTIVE[@]}"; do
    if printf '%s' "$seg" | grep -qE -- "$p"; then
      emit deny \
        "$(json_str "Blocked: this git command destroys work with no undo. Run it yourself if you truly intend to.")" \
        "$(json_str "Blocked by the git guardrail: '$seg'. This discards uncommitted or unreachable commits. Do not retry it and do not work around it. Ask the user to run it if it is genuinely required.")"
    fi
  done

  if printf '%s' "$seg" | grep -qE -- 'push' && ! printf '%s' "$seg" | grep -qE -- '--force-with-lease'; then
    if printf '%s' "$seg" | grep -qE -- '--force|[[:space:]]-f([[:space:]]|$)'; then
      emit deny \
        "$(json_str "Blocked: force push overwrites remote history.")" \
        "$(json_str "Blocked by the git guardrail: '$seg'. Force push overwrites remote history. Use --force-with-lease and ask the user to run it.")"
    fi
  fi

  if printf '%s' "$seg" | grep -qE -- '(^|[[:space:]])push([[:space:]]|$)'; then
    emit ask \
      "$(json_str "Confirm push to a remote: $seg")" \
      "$(json_str "This push needs human confirmation before it publishes.")"
  fi
done <<<"$SEGMENTS"

allow
