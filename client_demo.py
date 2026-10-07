"""Classify climate, list open bays, plant a bay and log readings through the API.

Usage:
    python client_demo.py                             # local service on port 8000
    python client_demo.py https://<your-service-url>  # hosted service; set PIXELTABLE_API_KEY first

Standard library only. If PIXELTABLE_API_KEY is set it is sent as the X-api-key header.
Exits non-zero if any call returns an unexpected status code.
"""
import concurrent.futures as cf
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000').rstrip('/')
API_KEY = os.environ.get('PIXELTABLE_API_KEY')
HERE = Path(__file__).resolve().parent
FAILURES: list[str] = []


def _send(req: urllib.request.Request) -> tuple[int, object]:
    if API_KEY:
        req.add_header('X-api-key', API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            if 'json' in (resp.headers.get('Content-Type') or ''):
                return resp.status, json.loads(raw or b'null')
            return resp.status, f'<{len(raw)} bytes {resp.headers.get("Content-Type")}>'
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:300]


def call(method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    data = json.dumps(body).encode() if body is not None else None
    return _send(urllib.request.Request(BASE + path, data=data, method=method,
                                        headers={'Content-Type': 'application/json'}))


def upload(path: str, fields: dict, files: dict) -> tuple[int, object]:
    """multipart/form-data POST: fields are form values, files maps field name -> local file path."""
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, fp in files.items():
        fp = Path(fp)
        ctype = mimetypes.guess_type(fp.name)[0] or 'application/octet-stream'
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fp.name}"\r\n'
                     f'Content-Type: {ctype}\r\n\r\n'.encode() + fp.read_bytes() + b'\r\n')
    body = b''.join(parts) + f'--{boundary}--\r\n'.encode()
    return _send(urllib.request.Request(BASE + path, data=body, method='POST',
                                        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}))


def check(label: str, code: int, out: object, expect: int = 200):
    print(f'{label:<36} {code}  {json.dumps(out)[:180]}')
    if code != expect:
        FAILURES.append(f'{label}: got {code}, expected {expect}')
    return out


def show(label: str, method: str, path: str, body: dict | None = None, expect: int = 200):
    code, out = call(method, path, body)
    return check(label, code, out, expect)


def parallel(label: str, n: int, fn) -> list:
    with cf.ThreadPoolExecutor(max_workers=min(n, 16)) as pool:
        results = list(pool.map(fn, range(n)))
    codes = sorted({c for c, _ in results})
    print(f'{label:<36} {n} calls, status codes: {codes}')
    if codes != [200]:
        FAILURES.append(f'{label}: status codes {codes}')
    return results


def q(s: str) -> str:
    return urllib.parse.quote(s)


show('climate band for 33 C / 88 %', 'POST', '/climate-band', {'temp_c': 33.0, 'humidity_pct': 88.0})
show('open bays in the north zone', 'GET', '/bays/open?zone=north')
show('add a bay', 'POST', '/bays', {'bay_id': 'C-01', 'zone': 'east', 'crop': None, 'status': 'open'})
show('plant A-12 with lettuce', 'POST', '/bays/status', {'bay_id': 'A-12', 'status': 'planted', 'crop': 'lettuce'})
show('record the planting', 'POST', '/plantings', {'bay_id': 'A-12', 'crop': 'lettuce', 'planted_on': '2026-10-04', 'status': 'seeded'})
parallel('10 sensor readings', 10, lambda i: call('POST', '/readings', {
    'bay_id': 'A-12', 'taken_at': f'2026-10-04T{8 + i:02d}:00', 'temp_c': 16.0 + i * 1.8, 'humidity_pct': 60.0 + i * 3}))
show('A-12 climate history', 'GET', '/bays/climate?bay_id=A-12')
show('north zone after planting', 'GET', '/bays/open?zone=north')


if FAILURES:
    print('\nFAILED:', *FAILURES, sep='\n  ')
    sys.exit(1)
print('\nall calls OK')
