#!/usr/bin/env python3
"""Local oracle for unpublished SONiC gNMI empty UserAuth fail-open.

ToR plaintext :18080 and DPU insecure TLS :18081 both skip authenticate()
when UserAuth is empty after setupFlags unsets cert mode with no ca_crt.
Writes stay compiled in (ENABLE_NATIVE_WRITE). Negative: password UserAuth
with no creds is Unauthenticated. Loopback only. No shells.
"""
from __future__ import annotations

import os
import sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
TOR = os.environ.get("TOR_ADDR", "127.0.0.1:18080")
DPU = os.environ.get("DPU_ADDR", "127.0.0.1:18081")
CERT = os.path.join(RUN_DIR, "certs", "server.crt")
WITNESS = "SONIC-GNMI-NOAUTH-WITNESS"


def fail(msg: str) -> None:
    print(f"FAIL SONIC-GNMI-NOAUTH {msg}", flush=True)
    raise SystemExit(1)


def encode_varint(n: int) -> bytes:
    out = bytearray()
    while n > 0x7F:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)


def decode_varint(buf: bytes, i: int) -> tuple[int, int]:
    shift = 0
    n = 0
    while True:
        if i >= len(buf):
            raise ValueError("truncated varint")
        b = buf[i]
        i += 1
        n |= (b & 0x7F) << shift
        if b < 0x80:
            return n, i
        shift += 7


def encode_check_request(require_password: bool = False) -> bytes:
    if not require_password:
        return b""
    return b"\x08\x01"


def decode_check_reply(buf: bytes) -> dict:
    out: dict[int, object] = {}
    i = 0
    while i < len(buf):
        key, i = decode_varint(buf, i)
        field, wt = key >> 3, key & 7
        if wt == 0:
            v, i = decode_varint(buf, i)
            out[field] = v
        elif wt == 2:
            ln, i = decode_varint(buf, i)
            out[field] = buf[i : i + ln]
            i += ln
        else:
            fail(f"unexpected protobuf wire type {wt}")
    def as_str(val: object) -> str:
        if isinstance(val, (bytes, bytearray)):
            return val.decode()
        return ""

    return {
        "witness": as_str(out.get(1, b"")),
        "auth_enabled": bool(out.get(2, 0)),
        "enable_native_write": bool(out.get(3, 0)),
        "enable_translib_write": bool(out.get(4, 0)),
        "user_auth_any": bool(out.get(5, 0)),
        "mode": as_str(out.get(6, b"")),
    }


def call_check(target: str, tls: bool, require_password: bool = False, timeout: float = 8.0):
    import grpc

    options = (
        ("grpc.enable_http_proxy", 0),
        ("grpc.ssl_target_name_override", "localhost"),
    )
    if tls:
        with open(CERT, "rb") as fh:
            creds = grpc.ssl_channel_credentials(root_certificates=fh.read())
        channel = grpc.secure_channel(target, creds, options=options)
    else:
        channel = grpc.insecure_channel(target, options=(("grpc.enable_http_proxy", 0),))
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout)
        method = channel.unary_unary(
            "/probe.Probe/Check",
            request_serializer=lambda x: x,
            response_deserializer=lambda x: x,
        )
        raw = method(encode_check_request(require_password), timeout=timeout, metadata=())
        return decode_check_reply(raw)
    finally:
        channel.close()


def expect_open(label: str, target: str, tls: bool, mode: str) -> None:
    try:
        reply = call_check(target, tls=tls, require_password=False)
    except Exception as exc:
        fail(f"{label} check error {type(exc).__name__}: {exc}")
    print(
        f"IOC {label}-check witness={reply['witness']} auth_enabled={str(reply['auth_enabled']).lower()} "
        f"enable_native_write={str(reply['enable_native_write']).lower()} "
        f"user_auth_any={str(reply['user_auth_any']).lower()} mode={reply['mode']}",
        flush=True,
    )
    if reply["witness"] != WITNESS:
        fail(f"{label} missing witness got={reply['witness']!r}")
    if reply["auth_enabled"]:
        fail(f"{label} auth_enabled true")
    if not reply["enable_native_write"]:
        fail(f"{label} enable_native_write false")
    if not reply["enable_translib_write"]:
        fail(f"{label} enable_translib_write false")
    if reply["user_auth_any"]:
        fail(f"{label} user_auth_any true")
    if reply["mode"] != mode:
        fail(f"{label} mode={reply['mode']!r} expected={mode!r}")


def expect_closed(label: str, target: str, tls: bool) -> None:
    import grpc

    try:
        reply = call_check(target, tls=tls, require_password=True)
    except grpc.RpcError as exc:
        code = exc.code().name if hasattr(exc, "code") else "RPC"
        print(f"IOC {label}-negative status={code}", flush=True)
        if exc.code() == grpc.StatusCode.OK:
            fail(f"{label} password mode returned OK")
        return
    except Exception as exc:
        fail(f"{label} negative unexpected {type(exc).__name__}: {exc}")
    fail(f"{label} password mode succeeded reply={reply}")


def main() -> None:
    try:
        import grpc  # noqa: F401
    except ImportError:
        fail("grpcio not installed")
    if not os.path.isfile(CERT):
        fail(f"missing lab TLS cert {CERT}")

    print(f"IOC tor-connect {TOR} plaintext no-metadata", flush=True)
    expect_open("tor", TOR, tls=False, mode="tor")
    print(f"IOC dpu-connect {DPU} tls-insecure no-client-cert no-metadata", flush=True)
    expect_open("dpu", DPU, tls=True, mode="dpu")
    expect_closed("tor", TOR, tls=False)
    expect_closed("dpu", DPU, tls=True)
    print(
        f"SUCCESS SONIC-GNMI-NOAUTH who=unauth tor=18080 dpu=18081 {WITNESS}",
        flush=True,
    )


if __name__ == "__main__":
    main()
