#!/usr/bin/env bash
# Creates a throwaway repo with three tickets for the orchestrate pilots.
# Usage: pilot-fixture.sh <target-dir>   (dir must not exist)
set -euo pipefail
dir="${1:?target dir}"
[ -e "$dir" ] && { echo "refusing: $dir exists" >&2; exit 1; }
mkdir -p "$dir/.scratch/greet/issues" "$dir/tests"
cd "$dir"
git init -q -b main
cat > greet.py <<'EOF'
def greet(name):
    raise NotImplementedError
EOF
cat > tests/test_greet.py <<'EOF'
from greet import greet
def test_placeholder():
    assert callable(greet)
EOF
cat > pytest.ini <<'EOF'
[pytest]
testpaths = tests
pythonpath = .
EOF
printf '__pycache__/\n.pytest_cache/\n' > .gitignore
mk() { # NN slug title blocked body
cat > ".scratch/greet/issues/$1-$2.md" <<EOF
# $3

**Blocked by:** $4

**Status:** ready-for-agent

$5

## Comments
EOF
}
mk 01 hello "greet returns a greeting" "None (can start immediately)" "- [ ] \`greet('Ada')\` returns \`'Hello, Ada!'\`
- [ ] a test in \`tests/test_greet.py\` covers it"
mk 02 shout "shout upper-cases a greeting" "None (can start immediately)" "- [ ] add \`shout(name)\` in \`greet.py\` returning \`'HELLO, ' + name.upper() + '!'\`
- [ ] a test in \`tests/test_greet.py\` covers it"
mk 03 polite "greet accepts an optional honorific" "01" "- [ ] \`greet('Ada', honorific='Dr.')\` returns \`'Hello, Dr. Ada!'\`
- [ ] \`greet('Ada')\` still returns \`'Hello, Ada!'\`
- [ ] tests cover both"
cat > .scratch/greet/tickets.md <<'EOF'
# Tickets: greet

Generated index — resolves to the issue files below. Source of truth is `issues/`; refresh on publish, on a /triage Status change, or once after each merge in /implement-spec.

| # | Title | Summary | Status | Blocked by |
|---|---|---|---|---|
| [01](issues/01-hello.md) | greet returns a greeting | Implement greet | ready-for-agent | None |
| [02](issues/02-shout.md) | shout upper-cases a greeting | Add shout | ready-for-agent | None |
| [03](issues/03-polite.md) | greet accepts an optional honorific | Extend greet | ready-for-agent | 01 |
EOF
git add -A && git commit -qm "fixture: three tickets for the orchestrate pilot"
echo "fixture ready at $dir"
