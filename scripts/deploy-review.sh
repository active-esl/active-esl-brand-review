#!/usr/bin/env bash
# Build a static tree and deploy to the Cloudflare Worker review tip.
# Live GitHub Pages (main → active-esl.com) is untouched.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
# shellcheck disable=SC1091
[[ -s "$NVM_DIR/nvm.sh" ]] && . "$NVM_DIR/nvm.sh"
nvm use 22 >/dev/null

export CLOUDFLARE_API_TOKEN
CLOUDFLARE_API_TOKEN="$(~/.cursor-secrets/bin/resolve-secret.sh get ACTIVE_ESL_CLOUDFLARE_API_TOKEN)"
export CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_ACCOUNT_ID="$(~/.cursor-secrets/bin/resolve-secret.sh get ACTIVE_ESL_CLOUDFLARE_ACCOUNT_ID)"

rm -rf _review_site
mkdir -p _review_site
python3 - <<'PY'
import shutil
from pathlib import Path
src, dst = Path("."), Path("_review_site")
ignore_names = {
    ".git", ".github", "_review_site", "_site", "node_modules",
    "scripts", "docs", "wrangler.toml", ".wrangler",
}
for child in src.iterdir():
    if child.name in ignore_names or child.name.startswith(".git"):
        continue
    if child.name.endswith(".md") and child.name not in {"llms.txt"}:
        # Keep README out of public tip; llms.txt is intentional
        if child.name == "README.md":
            continue
    target = dst / child.name
    if child.is_dir():
        shutil.copytree(child, target, dirs_exist_ok=True)
    else:
        shutil.copy2(child, target)
# Review tip must not claim the production CNAME
cname = dst / "CNAME"
if cname.exists():
    cname.unlink()
(dst / ".nojekyll").touch()
print("prepared", dst, "entries", len(list(dst.iterdir())))
PY

npx --yes wrangler@4 deploy

python3 - <<'PY'
import json, os, urllib.request

def api(method, url, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={
            "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.load(r)
    except Exception as e:
        raw = e.read().decode() if hasattr(e, "read") else str(e)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:500]}
        return getattr(e, "code", None), parsed

zone = "a28c3d1c97e7894523d42f7d41a4f068"
hostname = "review.active-esl.com"
target = "active-esl-website-review.active-esl.workers.dev"
script = "active-esl-website-review"

st, body = api("GET", f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records?name={hostname}")
recs = body.get("result") or []
if not recs:
    st, body = api(
        "POST",
        f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records",
        {"type": "CNAME", "name": hostname, "content": target, "proxied": True, "ttl": 1},
    )
    print("dns_create", st, "success", body.get("success"), "errors", body.get("errors"))
else:
    print("dns_ok", recs[0].get("type"), recs[0].get("content"), "proxied", recs[0].get("proxied"))

st, body = api("GET", f"https://api.cloudflare.com/client/v4/zones/{zone}/workers/routes")
routes = [r for r in (body.get("result") or []) if r.get("pattern", "").startswith(hostname)]
if not routes:
    st, body = api(
        "POST",
        f"https://api.cloudflare.com/client/v4/zones/{zone}/workers/routes",
        {"pattern": f"{hostname}/*", "script": script},
    )
    print("route_create", st, "success", body.get("success"), "errors", body.get("errors"))
else:
    print("route_ok", routes[0].get("pattern"), "→", routes[0].get("script"))

print("Review tip: https://review.active-esl.com/")
print("Workers.dev (may be disabled): https://%s" % target)
PY
