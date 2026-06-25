r"""
NUKE all proxy detection at the OS level for this process.

On Windows, urllib.request.getproxies() reads
HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings
from the registry.  Every Python HTTP library eventually calls this
function, so monkey-patching intermediate layers never sticks.

Replace it with a function that always returns {} — no proxy, ever.
"""

import os

for _key in (
    "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
    "ALL_PROXY", "all_proxy",
):
    os.environ.pop(_key, None)

# ── The ONE patch that actually matters ────────────────────────────
import urllib.request as _ur

_ur.getproxies = lambda: {}
_ur.proxy_bypass = lambda host: True
_ur.proxy_bypass_environment = lambda host: True
