#!/usr/bin/env python3
import hashlib
import html
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

BASELINE_SHA = "243d3556292258e137b3b709a0b9d3efbd7283e5"
BASELINE_SHORT_SHA = BASELINE_SHA[:8]
BASELINE_VERSION = "0.4.30"
APK_SHA256 = "857278af9c71b57933bf182900cf254d2ada150fed1c6c5d523c62dc8c9e0f48"
RELEASE_TAG = "android-field-b30-frozen"
RELEASE_API = "https://api.github.com/repos/stefm78/recit-audioguide/releases/tags/android-field-b30-frozen"
QUALIFICATION_REL = Path("qualification/ios-safari-field-b30")
RUNTIME_PREFIX = "assets/public/"


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "recit-audioguide-ios-safari-field-b30-qualification",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def runtime_tree_digest(runtime: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    files = 0
    total_bytes = 0
    for path in sorted(p for p in runtime.rglob("*") if p.is_file()):
        rel = path.relative_to(runtime).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(rel)
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
        files += 1
        total_bytes += len(data)
    return digest.hexdigest(), files, total_bytes


def extract_runtime(apk_bytes: bytes, runtime: Path) -> None:
    with tempfile.NamedTemporaryFile(suffix=".apk") as handle:
        handle.write(apk_bytes)
        handle.flush()
        with zipfile.ZipFile(handle.name) as archive:
            names = archive.namelist()
            if f"{RUNTIME_PREFIX}index.html" not in names:
                raise RuntimeError(f"B30 APK does not contain {RUNTIME_PREFIX}index.html")
            members = [name for name in names if name.startswith(RUNTIME_PREFIX) and not name.endswith("/")]
            if not members:
                raise RuntimeError("B30 APK contains no packaged Web runtime")
            for name in members:
                rel = Path(name[len(RUNTIME_PREFIX):])
                if not rel.parts or ".." in rel.parts:
                    raise RuntimeError(f"Unsafe runtime path in APK: {name}")
                target = runtime / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))


def assert_runtime_contract(runtime: Path) -> None:
    required = [
        runtime / "index.html",
        runtime / "catalog.json",
        runtime / "assets" / "app.js",
        runtime / "assets" / "styles.css",
        runtime / "s" / "seville-discovery" / "index.html",
        runtime / "data" / "seville-discovery" / "series.json",
    ]
    missing = [str(path.relative_to(runtime)) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"B30 runtime missing required files: {missing}")

    home = (runtime / "index.html").read_text(encoding="utf-8")
    required_markers = [
        f"FIELD BUILD {BASELINE_VERSION}",
        BASELINE_SHORT_SHA,
        "recit-home-library",
        "recit:library:hidden:v1",
        "Bibliothèque",
    ]
    absent = [marker for marker in required_markers if marker not in home]
    if absent:
        raise RuntimeError(f"B30 runtime identity/library markers missing: {absent}")

    for path in runtime.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "serviceWorker.register" in text or "navigator.serviceWorker.register" in text:
            raise RuntimeError(f"Unexpected service-worker registration in frozen B30 runtime: {path.relative_to(runtime)}")


def write_landing_page(target: Path, runtime_digest: str, file_count: int, total_bytes: int) -> None:
    identity = f"SAFARI FIELD B30 · {BASELINE_SHORT_SHA}"
    target.write_text(
        f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="robots" content="noindex,nofollow">
  <title>{html.escape(identity)}</title>
  <style>
    :root {{ color-scheme: dark; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin:0; background:#0f1115; color:#f4f1e8; }}
    main {{ max-width:760px; margin:0 auto; padding:max(28px, env(safe-area-inset-top)) 20px max(32px, env(safe-area-inset-bottom)); }}
    .eyebrow {{ color:#d9b35c; font-weight:800; letter-spacing:.08em; font-size:.78rem; }}
    h1 {{ margin:.45rem 0 1rem; font-size:clamp(1.7rem,8vw,2.7rem); line-height:1.05; }}
    .card {{ border:1px solid #343945; border-radius:18px; padding:18px; background:#171a21; margin:16px 0; }}
    .go {{ display:inline-block; margin-top:8px; padding:13px 17px; border-radius:999px; background:#f4f1e8; color:#111; font-weight:800; text-decoration:none; }}
    code {{ font-size:.78rem; word-break:break-all; }}
    li {{ margin:.55rem 0; }}
  </style>
</head>
<body>
<main>
  <div class="eyebrow">QUALIFICATION IPHONE · SAFARI/WEBKIT</div>
  <h1>{html.escape(identity)}</h1>
  <div class="card">
    <strong>Périmètre</strong>
    <p>Cette surface qualifie le runtime Web B30 dans Safari sur iPhone. Elle ne qualifie pas une application iOS native.</p>
    <p><strong>Online uniquement.</strong> Aucun Service Worker, manifest PWA ou mécanisme offline n'est ajouté pour ce gate.</p>
    <a class="go" href="./runtime/">Ouvrir le runtime B30 dans Safari</a>
  </div>
  <div class="card">
    <strong>Gate physique IOS_SAFARI_FIELD_B30</strong>
    <ol>
      <li>Safe areas et affichage général.</li>
      <li>Bibliothèque : ouverture, filtres, masquer/réafficher et persistance.</li>
      <li>Navigation vers Séville et au moins un autre parcours.</li>
      <li>Lecture audio, pause/reprise et comportement arrière-plan/écran verrouillé observable dans Safari.</li>
      <li>Fermeture puis réouverture de Safari : reprise et préférences persistantes.</li>
    </ol>
  </div>
  <div class="card">
    <strong>Provenance figée</strong>
    <p>Commit B30 : <code>{BASELINE_SHA}</code></p>
    <p>APK SHA-256 : <code>{APK_SHA256}</code></p>
    <p>Runtime extrait sans modification : <code>{runtime_digest}</code></p>
    <p>{file_count} fichiers · {total_bytes} octets.</p>
  </div>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def publish(dist: Path) -> Path:
    release = json.loads(request_bytes(RELEASE_API).decode("utf-8"))
    if release.get("tag_name") != RELEASE_TAG:
        raise RuntimeError(f"Unexpected release tag: {release.get('tag_name')}")
    if release.get("target_commitish") != BASELINE_SHA:
        raise RuntimeError(
            f"Frozen B30 release target drifted: {release.get('target_commitish')} != {BASELINE_SHA}"
        )
    assets = {asset.get("name"): asset for asset in release.get("assets", [])}
    apk_asset = assets.get("recit-seville-field.apk")
    if not apk_asset or not apk_asset.get("browser_download_url"):
        raise RuntimeError("B30 release APK asset is missing")

    apk_bytes = request_bytes(apk_asset["browser_download_url"])
    actual_apk_sha = sha256_bytes(apk_bytes)
    if actual_apk_sha != APK_SHA256:
        raise RuntimeError(f"B30 APK SHA drifted: {actual_apk_sha} != {APK_SHA256}")

    qualification = dist / QUALIFICATION_REL
    runtime = qualification / "runtime"
    if qualification.exists():
        shutil.rmtree(qualification)
    runtime.mkdir(parents=True, exist_ok=True)
    extract_runtime(apk_bytes, runtime)
    assert_runtime_contract(runtime)
    runtime_digest, file_count, total_bytes = runtime_tree_digest(runtime)

    write_landing_page(qualification / "index.html", runtime_digest, file_count, total_bytes)
    manifest = {
        "schema": "recit.qualification.ios-safari-field-b30.v1",
        "status": "HUMAN_GATE",
        "gate": "IOS_SAFARI_FIELD_B30",
        "baseline_commit": BASELINE_SHA,
        "baseline_version": BASELINE_VERSION,
        "source_release_tag": RELEASE_TAG,
        "source_apk_sha256": APK_SHA256,
        "runtime_tree_sha256": runtime_digest,
        "runtime_file_count": file_count,
        "runtime_total_bytes": total_bytes,
        "runtime_modified_after_extraction": False,
        "scope": "SAFARI_WEBKIT_ONLINE_ONLY",
        "native_ios_qualified": False,
        "offline_safari": "OUT_OF_SCOPE",
        "service_worker_added": False,
        "pwa_manifest_added": False,
    }
    (qualification / "qualification.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Published IOS_SAFARI_FIELD_B30 from exact APK {APK_SHA256[:12]}…: "
        f"{file_count} runtime files, tree {runtime_digest[:12]}…"
    )
    return qualification


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    out = Path(os.environ.get("RECIT_DIST", root / "dist"))
    publish(out)
