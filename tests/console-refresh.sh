#!/bin/bash
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
export CALL_LOG="$tmp/calls"
mkdir "$tmp/bin"
cat > "$tmp/bin/loginctl" <<'MOCK'
#!/bin/sh
case "$1" in
  list-sessions) printf '1 0 root seat0
2 0 root -
3 1000 user seat1
';;
  show-session) case "$2" in 1) echo tty1;; 2) echo pts/0;; 3) echo tty2;; esac;;
  terminate-session) echo "terminate $2" >> "$CALL_LOG";;
  *) exit 2;;
esac
MOCK
cat > "$tmp/bin/systemctl" <<'MOCK'
#!/bin/sh
printf '%s %s
' "$1" "$2" >> "$CALL_LOG"
MOCK
chmod +x "$tmp/bin/"*
PATH="$tmp/bin:$PATH" sh "$root/bin/theater-kiosk-restart"
printf 'terminate 1
restart getty@tty1.service
' > "$tmp/expected"
diff -u "$tmp/expected" "$CALL_LOG"
echo 'PASS: console restart targets tty1 only, preserving SSH and other consoles'
