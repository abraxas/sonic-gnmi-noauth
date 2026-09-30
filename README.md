<p align="center">
  <img src="header.png" alt="Abraxas Labs — sonic-gnmi-noauth" width="100%">
</p>

<p align="center">
  <a href="https://abraxaslabs.tech"><strong>abraxaslabs.tech</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas">github.com/abraxas</a>
  &nbsp;·&nbsp;
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas/sonic-gnmi-noauth">sonic-gnmi-noauth</a>
</p>

# sonic-gnmi-noauth

**SONiC gNMI (sonic-gnmi)** `master f13a08e0440f` — SONiC Foundation / sonic-net

Unpublished SONiC source finding: the gnmi launcher still passes `--client_auth cert` as a fail-closed default, then `setupFlags` unsets cert mode when `ca_crt` is empty. `authenticate()` treats empty `UserAuth` as success. Native and translib writes are compiled in, so unauthenticated gNMI Set and gNOI writes are registered. SmartSwitch DPU with no certs is remote on `:8080`. Default ToR with no certs is loopback. Community SONiC NOS — not Dell Enterprise SONiC, not SonicWall SonicOS.

| | |
|---|---|
| ID | Unpublished SONiC source finding #1 (no CVE yet) |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) |
| CVSS | **Critical: 9.8** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` |
| Product | [SONiC gNMI (sonic-gnmi)](https://github.com/sonic-net/sonic-gnmi) |
| Affected | sonic-gnmi **through master f13a08e0440f** (inclusive); launcher in [sonic-buildimage](https://github.com/sonic-net/sonic-buildimage) `9495839742e4` |
| Patched | vendor patch — see references |
| Auth | unauthenticated (see source map) |
| License | [GNU Affero GPL v3.0](LICENSE) |
| Lab | `127.0.0.1` only · vendor/client disclosure pack, not a scanner |

---

## Advisory (from the source map)

telemetry.go 345-347 Unset cert without CA; telemetry.go ~592 UserAuth copy only in TLS branch; server.go 858-861 empty UserAuth success; server.go 370-376 gNOI writes gated on write flags; gnmi-native.sh 174-182 fail-closed --client_auth cert; constants_native_write.go ENABLE_NATIVE_WRITE=true.

---

## Entry

- **Method:** `gRPC`
- **Path:** `/gnmi.gNMI/Set`
- **Router:** `/gnmi.gNMI/Set` and `/gnoi.debug.Debug`. gnmi-native.sh still passes `--client_auth cert` as fail-closed; setupFlags Unsets cert when CaCert is empty; authenticate() returns nil on empty UserAuth. ENABLE_NATIVE_WRITE compiled in.
- **Notes:** Unauthenticated unpublished SONiC #1 CWE-306 sonic-gnmi f13a08e0440f. DPU `--insecure --allow_no_client_auth` no CA is remote `:8080`. Default ToR `--noTLS` bind `127.0.0.1:8080` host net. Lab oracle SONIC-GNMI-NOAUTH-WITNESS on write-path authenticate skip, not a gNOI docker gadget. Vendor: encrypt to security@lists.sonicfoundation.dev. Do **not** open a public GitHub issue on sonic-net/*.

### Call chain

- `gnmi-native.sh USER_AUTH default cert, no ca_crt`
- `telemetry setupFlags: UserAuth.Set(cert) then Unset(cert) because CaCert==""`
- `startGNMIServer copies cfg.UserAuth only in the TLS branch (ToR --noTLS never copies)`
- `authenticate(): unix-peer skip, then empty UserAuth.Any() returns ctx, nil`
- `/gnmi.gNMI/Set` and `/gnoi.debug.Debug` registered because ENABLE_NATIVE_WRITE / ENABLE_TRANSLIB_WRITE
- `lab Probe.Check(writeAccess=true)` returns SONIC-GNMI-NOAUTH-WITNESS; password UserAuth with no creds is Unauthenticated

### Lab preconditions

- sonic-gnmi f13a08e0440f with ENABLE_NATIVE_WRITE=y ENABLE_TRANSLIB_WRITE=y
- ToR: `--noTLS --bind_address 127.0.0.1 --port 8080 --client_auth cert` and empty ca_crt
- DPU: `--insecure --allow_no_client_auth --client_auth cert` and empty ca_crt
- Attacker can TCP the listener (loopback on default ToR, `:8080` on DPU no-cert)

### Witness

SONIC-GNMI-NOAUTH-WITNESS

### Not success

- eval/base64/system payload
- reverse shell
- gNOI Debug docker run gadget
- nsenter / docker-breakout in the pack
- authenticate() still requiring cert/password/jwt
- Probe.Check returning OK when UserAuth password is enabled and no creds

---

## Patch / remediation

**Do this first:** Apply the vendor patch for **SONiC gNMI (sonic-gnmi)** and the gnmi container launcher in sonic-buildimage. See references.

**Verify after upgrade**

- Re-run `sonic-gnmi-noauth-Abraxas-Labs.py` against the patched extracts: the mapped witness must **not** appear.
- Confirm the vendor advisory / changeset in the deployed tree (see references).
- A WAF signature is delay, not a patch.

**If you cannot update immediately**

- Provision GNMI server certs and a CA so `--ca_crt` is set and cert mode is not unset.
- Do not run SmartSwitch DPU no-cert (`--insecure --allow_no_client_auth` with empty CA) on a reachable `:8080`.
- Hunt for unauthenticated gNMI Set / gNOI Debug on `:8080` (no JWT / PAM / client cert).

---

## Reproduction (authorized lab)

Target **only** `127.0.0.1:18080` (ToR plaintext) and `127.0.0.1:18081` (DPU TLS-insecure). Do not point this script at the internet.

The lab is a thin gRPC that calls SHA256-checked extracts of `authenticate` and the `setupFlags` CA-unset block from sonic-gnmi `f13a08e0440f`. It does **not** ship a gNOI Debug docker gadget.

```bash
cd lab
./run.sh
```

Or, with the stack already up (grpcio required):

```bash
python3 sonic-gnmi-noauth-Abraxas-Labs.py
```

Success is the **witness** above on both listeners (`auth_enabled=false`, `enable_native_write=true`) plus Unauthenticated when password UserAuth is forced. Generic 200 HTML is not it. This pack does **not** include a reverse shell or nsenter payload.

---

## Lab images

Loopback stack used to reproduce. Dockerfile builds the extracted telemetry flags + `authenticate()` oracle from pin files.

- [`lab/docker-compose.yml`](lab/docker-compose.yml)
- [`lab/Dockerfile`](lab/Dockerfile)
- [`lab/run.sh`](lab/run.sh)
- [`lab/check_extracts.py`](lab/check_extracts.py)
- [`lab/poc.py`](lab/poc.py)
- [`lab/pin/`](lab/pin/) — sonic-gnmi / gnmi-native.sh extracts
- [`lab/lab/`](lab/lab/) — Go module (authenticate + setupFlags + probe)
- [`lab/certs/`](lab/certs/) — lab TLS material for the DPU listener

Publish nothing except `127.0.0.1`.

---

## References

- [github.com/sonic-net/sonic-gnmi](https://github.com/sonic-net/sonic-gnmi) pin f13a08e0440f
- [github.com/sonic-net/sonic-buildimage](https://github.com/sonic-net/sonic-buildimage) pin 9495839742e4 (`dockers/docker-sonic-gnmi/gnmi-native.sh`)
- Vendor intake: encrypt to [security@lists.sonicfoundation.dev](mailto:security@lists.sonicfoundation.dev) ([SECURITY.md](https://github.com/sonic-net/SONiC/blob/master/SECURITY.md)). Do **not** open a public GitHub issue on sonic-net/*.

- Abraxas Labs: [abraxaslabs.tech](https://abraxaslabs.tech) · [github.com/abraxas](https://github.com/abraxas) · [@abraxas_null](https://x.com/abraxas_null)

---

## Records (structured)

```
# SONiC unpublished #1 — gNMI/gNOI empty UserAuth fail-open

CWE: CWE-306, CWE-287
Severity: Critical (DPU remote) / High (default ToR loopback)

## Description

The gnmi container launcher still passes `--client_auth cert` as a fail-closed default. `setupFlags` then unsets cert mode when `ca_crt` is empty. `authenticate()` treats empty `UserAuth` as success. Native and translib writes are compiled in, so unauthenticated gNMI Set and gNOI Debug/Reboot/File are registered.

Default ToR/leaf with no certs listens plaintext on loopback. SmartSwitch DPU with no certs serves ephemeral TLS on :8080 with optional client certs.

## Product

Community SONiC gNMI (`sonic-net/sonic-gnmi` f13a08e0440f), writes on (`ENABLE_NATIVE_WRITE=y`, `ENABLE_TRANSLIB_WRITE=y`). Lab oracle is `SONIC-GNMI-NOAUTH-WITNESS` on write-path `authenticate()` skip for both production flag sets. Not a gNOI docker gadget.

## Chain

1. Launcher defaults `user_auth=cert` and does not pass `--ca_crt` when certs are absent.
2. `setupFlags` sees empty CA and unsets cert authentication.
3. ToR `--noTLS` never copies `UserAuth` onto the server config (TLS-branch only). DPU `--insecure` copies the already-empty map.
4. `authenticate()` returns success for empty `UserAuth` on write RPCs.
5. Negative: `UserAuth` with `password` and no credentials is Unauthenticated, so the oracle is the real skip, not a stub that always succeeds.
```

---

## License

This disclosure pack is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE).

---

## Disclaimer

This pack is for **the vendor, the site owner, and licensed labs**. The script talks to `127.0.0.1`. Using it against systems you do not own is not authorized by Abraxas Labs. No warranty.

<p align="center">
  <a href="https://abraxaslabs.tech">abraxaslabs.tech</a> ·
  <a href="https://github.com/abraxas">github.com/abraxas</a> ·
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
</p>
