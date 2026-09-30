#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-sonic-gnmi-noauth}"
chmod +x poc.py

down() {
  echo "== docker compose down -v =="
  docker compose down -v --remove-orphans || true
}

PY=python3
if ! "$PY" -c "import grpc" 2>/dev/null; then
  echo "== venv grpcio =="
  if [[ ! -d .venv ]]; then
    "$PY" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  PY=python3
  pip install -q --upgrade pip
  pip install -q grpcio protobuf
fi

echo "== docker compose down (clean) =="
docker compose down -v --remove-orphans || true

echo "== docker compose up --build (loopback :18080/:18081) =="
up_ok=0
for attempt in $(seq 1 6); do
  if docker compose up -d --build; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=$attempt"
  sleep 12
done
if [[ "$up_ok" != 1 ]]; then
  echo "FAIL SONIC-GNMI-NOAUTH docker compose up" | tee poc-last-run.txt
  docker compose logs --tail=80 gnmi || true
  down
  exit 1
fi

echo "== wait for ToR :18080 and DPU :18081 =="
ok=0
for i in $(seq 1 60); do
  if "$PY" - <<'PY'
import socket, sys
for port in (18080, 18081):
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
    except OSError:
        sys.exit(1)
    finally:
        s.close()
sys.exit(0)
PY
  then
    echo "IOC gnmi-up tor=18080 dpu=18081"
    ok=1
    break
  fi
  echo "IOC wait i=$i"
  sleep 2
done
if [[ "$ok" != 1 ]]; then
  echo "FAIL SONIC-GNMI-NOAUTH listeners did not become ready" | tee poc-last-run.txt
  docker compose logs --tail=80 gnmi || true
  down
  exit 1
fi

echo "== poc.py =="
set +e
"$PY" poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if [[ "$rc" != 0 ]]; then
  echo "== gnmi logs (tail) ==" | tee -a poc-last-run.txt
  docker compose logs --tail=80 gnmi | tee -a poc-last-run.txt || true
fi
down
exit "$rc"
