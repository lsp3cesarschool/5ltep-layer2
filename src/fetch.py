"""Fetching CKAN resources: one request per resource and run, integrity recorded for the dashboard.

Every source of every rule is a CKAN resource (portal, dataset, exact resource name and format).
Sources that name the same resource are fetched once. For each resource the run records whether
the portal answered (`package_show`), whether exactly one resource matched, and what was
downloaded (HTTP status, bytes, SHA-256 of the bytes, ETag/Last-Modified). A failure is a result,
never a silent gap: the rules that need that resource are reported as not evaluated.

The download streams to disk (as in Layer 3, `ckan_source.py`); the file is read from disk after.
A file larger than the runner's disk would need Layer 1's streamed unzip (`stream_unzip`); not
needed for the resources used so far.
"""

from __future__ import annotations

import fnmatch
import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import requests

USER_AGENT = "5ltep-layer2 (research; https://github.com/lsp3cesarschool/5ltep-layer2)"
TIMEOUT_S = 60
RETRIES = 3
BACKOFF_S = 10.0

SESSION = requests.Session()
SESSION.headers["User-Agent"] = USER_AGENT

# Fetch states, in the order a fetch goes through them.
OK = "ok"
PORTAL_UNREACHABLE = "portal_unreachable"
RESOURCE_NOT_FOUND = "resource_not_found"
RESOURCE_AMBIGUOUS = "resource_ambiguous"
DOWNLOAD_FAILED = "download_failed"


@dataclass(frozen=True)
class ResourceKey:
    portal: str
    dataset: str
    name: str
    format: str

    @classmethod
    def of(cls, source: dict) -> "ResourceKey":
        return cls(source["portal"].rstrip("/"), source["dataset"],
                   source["resource"]["name"], source["resource"]["format"])

    @property
    def label(self) -> str:
        return f"{urlparse(self.portal).hostname} › {self.dataset} › {self.name}"


@dataclass
class Fetched:
    key: ResourceKey
    status: str = OK
    reason: str | None = None
    used_by: list[str] = field(default_factory=list)
    role: str = "secondary"                         # primary: the portal of this instance (portal.json)
    portal: dict = field(default_factory=dict)      # package_show: http status, seconds
    dataset: dict = field(default_factory=dict)     # title, organization, license, metadata_modified
    resource: dict = field(default_factory=dict)    # id, url, metadata of the matched resource
    download: dict = field(default_factory=dict)    # http status, bytes, sha256, etag, last_modified, seconds
    path: Path | None = None                        # local file, never published
    parts: list[dict] = field(default_factory=list)  # one per published file: name, path, resource, download

    def record(self) -> dict:
        return {"portal": self.key.portal, "dataset_name": self.key.dataset,
                "resource_name": self.key.name, "resource_format": self.key.format,
                "label": self.key.label, "role": self.role, "status": self.status, "reason": self.reason,
                "used_by": sorted(self.used_by), "package_show": self.portal, "dataset": self.dataset,
                "resource": self.resource, "download": self.download,
                "files": [{"file": p["name"], "url": p["resource"].get("url"), "resource_id": p["resource"].get("id"),
                           "bytes": p["download"].get("bytes"), "sha256": p["download"].get("sha256")} for p in self.parts]}


def _get(url: str, **kwargs) -> requests.Response:
    """GET with a few spaced retries for network errors and 5xx answers; 4xx is returned at once."""
    last: Exception | None = None
    for attempt in range(RETRIES):
        try:
            resp = SESSION.get(url, timeout=TIMEOUT_S, **kwargs)
            if resp.status_code < 500:
                return resp
            last = requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.close()
        except requests.RequestException as exc:
            last = exc
        if attempt < RETRIES - 1:
            time.sleep(BACKOFF_S * (attempt + 1))
    raise last


def _error(exc: Exception) -> str:
    if isinstance(exc, requests.exceptions.SSLError):
        return f"TLS: {exc}"[:300]
    if isinstance(exc, requests.Timeout):
        return f"tempo esgotado ({TIMEOUT_S} s)"
    if isinstance(exc, requests.ConnectionError):
        return f"sem conexão: {exc}"[:300]
    return f"{type(exc).__name__}: {exc}"[:300]


def fetch(key: ResourceKey, folder: Path) -> Fetched:
    out = Fetched(key)
    # 1. the portal: package_show of the dataset
    t0 = time.monotonic()
    try:
        resp = _get(f"{key.portal}/api/3/action/package_show", params={"id": key.dataset})
        out.portal = {"http_status": resp.status_code, "seconds": round(time.monotonic() - t0, 2)}
        if resp.status_code == 404:
            out.status, out.reason = RESOURCE_NOT_FOUND, f"dataset {key.dataset!r} não existe no portal"
            return out
        resp.raise_for_status()
        package = resp.json()["result"]
    except (requests.RequestException, ValueError, KeyError) as exc:
        out.portal.setdefault("seconds", round(time.monotonic() - t0, 2))
        out.portal["error"] = _error(exc)
        out.status, out.reason = PORTAL_UNREACHABLE, f"portal não respondeu: {_error(exc)}"
        return out
    out.dataset = {"title": package.get("title"), "organization": (package.get("organization") or {}).get("title"),
                   "license": package.get("license_title"), "metadata_modified": package.get("metadata_modified")}

    # 2. the resource with that name and format; with * ? or [...] in the name, every resource that matches
    #    (for example one resource per year), downloaded one after the other and read in name order
    pattern = any(ch in key.name for ch in "*?[")

    def name_matches(r):
        name = (r.get("name") or "").strip()
        return fnmatch.fnmatchcase(name, key.name.strip()) if pattern else name == key.name.strip()

    matches = [r for r in package.get("resources", [])
               if name_matches(r) and (r.get("format") or "").strip().upper() == key.format.strip().upper()]
    if not matches or (len(matches) > 1 and not pattern):
        available = [f"{r.get('name')} ({r.get('format')})" for r in package.get("resources", [])]
        out.status = RESOURCE_NOT_FOUND if not matches else RESOURCE_AMBIGUOUS
        out.reason = (f"{len(matches)} recursos com nome {key.name!r} e formato {key.format}; "
                      f"disponíveis: {available}")[:600]
        return out
    matches.sort(key=lambda r: (r.get("name") or ""))

    # 3. the bytes of each resource, streamed to disk with their SHA-256
    t_all = time.monotonic()
    for n, res in enumerate(matches):
        meta = {"id": res.get("id"), "url": res.get("url"), "name": res.get("name"),
                "metadata_modified": res.get("metadata_modified"), "last_modified": res.get("last_modified"),
                "size_declared": res.get("size")}
        path = folder / f"{hashlib.sha256(repr(key).encode()).hexdigest()[:16]}-{n}.bin"
        sha, size, t0 = hashlib.sha256(), 0, time.monotonic()
        download: dict = {}
        try:
            resp = _get(res["url"], stream=True)
            download = {"http_status": resp.status_code, "etag": resp.headers.get("ETag"),
                        "last_modified": resp.headers.get("Last-Modified"),
                        "content_type": resp.headers.get("Content-Type"), "served_by": urlparse(resp.url).hostname}
            resp.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    fh.write(chunk)
                    sha.update(chunk)
                    size += len(chunk)
            resp.close()
        except (requests.RequestException, OSError) as exc:
            path.unlink(missing_ok=True)
            for p in out.parts:
                p["path"].unlink(missing_ok=True)
            download["error"] = _error(exc)
            out.download = download
            out.status, out.reason = DOWNLOAD_FAILED, f"download de {res.get('name')!r} falhou: {_error(exc)}"
            return out
        seconds = time.monotonic() - t0
        download.update(bytes=size, sha256=sha.hexdigest(), seconds=round(seconds, 2),
                        mb_per_s=round(size / 1e6 / seconds, 3) if seconds > 0 else None)
        name = PurePosixPath(unquote(urlparse(res.get("url") or "").path)).name or (res.get("name") or "")
        out.parts.append({"name": name, "path": path, "resource": meta, "download": download})

    # one resource: its own metadata; several: the list, total bytes and a SHA-256 over the parts' hashes
    if len(out.parts) == 1:
        out.resource, out.download, out.path = out.parts[0]["resource"], out.parts[0]["download"], out.parts[0]["path"]
    else:
        seconds = time.monotonic() - t_all
        size = sum(p["download"]["bytes"] for p in out.parts)
        out.resource = {"count": len(out.parts), "names": [p["resource"]["name"] for p in out.parts],
                        "metadata_modified": max((p["resource"].get("metadata_modified") or "") for p in out.parts) or None}
        out.download = {"http_status": 200, "bytes": size, "seconds": round(seconds, 2),
                        "mb_per_s": round(size / 1e6 / seconds, 3) if seconds > 0 else None,
                        "sha256": hashlib.sha256("".join(p["download"]["sha256"] for p in out.parts).encode()).hexdigest(),
                        "sha256_note": "SHA-256 dos SHA-256 de cada arquivo, na ordem dos nomes"}
    return out
