"""Renames the viewer in the Fluent locales, for Confluence Viewer.

Run it after every merge from Aurora Viewer's main branch, on the three
catalogues (a merge conflict there is solved by taking upstream's file, then
running this again):

    python -I scripts/branding/rebrand-locales.py crates/aurora-i18n/locales/en.ftl \
        crates/aurora-i18n/locales/fr.ftl crates/aurora-i18n/locales/ja.ftl

- "Aurora" becomes "Confluence" where the word names the viewer.
- Feature, place and preset names keep Aurora's: the offline demo world,
  photo looks, avatar parts, the in-world bridge, the "#Aurora" inventory
  folder the AO code reads, etc. In the demo's strings only the viewer's own
  name ("Aurora Viewer") changes.
- The login tagline says the viewer is for OpenSim as well as Second Life.

The script is idempotent: a second run changes nothing.
"""

import io
import re
import sys

PROTECT_KEYS = ("demo-", "common-aurora-demo", "common-aurora-plaza", "photo-looks-", "world-appearance-aurora", "import-preview-aurora")
PROTECT_PHRASES = [
    "#Aurora", "Aurora ＡＯ",
    "Aurora bridge", "Aurora Bridge", "Aurora Plaza", "Aurora plaza", "Aurora Library", "Aurora Demo", "Aurora demo",
    "Aurora Démo", "Aurora LiveMesh", "Aurora Lagoon", "Aurora AO", "Aurora water", "Aurora silhouette", "Aurora 3D",
    "Aurora Team", "Aurora Club", "Aurora Builders", "Aurora media", "Aurora skin", "Aurora hair", "Aurora beach",
    "Aurora Beach", "Aurora lantern", "Aurora experience",
    # a feature that regions set for every viewer (environment codes)
    "Aurora Weather", "Aurora weather", "Météo Aurora", "météo Aurora", "Aurora の天気",
]
# Whole values replaced by key, in every catalogue (the key's own language).
OVERRIDES = {
    "en.ftl": {
        "ui-login-second-life-client-rust-vulkan": "Second Life & OpenSim client  ·  Rust  ·  Vulkan",
        "ui-login-second-life-client-rust-metal": "Second Life & OpenSim client  ·  Rust  ·  Metal",
    },
    "fr.ftl": {
        "ui-login-second-life-client-rust-vulkan": "Client Second Life & OpenSim  ·  Rust  ·  Vulkan",
        "ui-login-second-life-client-rust-metal": "Client Second Life & OpenSim  ·  Rust  ·  Metal",
    },
    "ja.ftl": {
        "ui-login-second-life-client-rust-vulkan": "Second Life・OpenSimクライアント・Rust・Vulkan",
        "ui-login-second-life-client-rust-metal": "Second Life・OpenSimクライアント・Rust・Metal",
    },
}
KEY = re.compile(r"^([A-Za-z0-9_-]+)\s*=\s*")
WORD = re.compile(r"(?<![A-Za-z])Aurora(?![A-Za-z])")


def rename(text):
    # the program's file name (scripts/package.ps1 ships confluence-viewer.exe)
    text = text.replace("aurora-viewer.exe", "confluence-viewer.exe")
    held = {}
    for i, phrase in enumerate(PROTECT_PHRASES):
        token = f"\x00{i}\x00"
        if phrase in text:
            held[token] = phrase
            text = text.replace(phrase, token)
    # French elision: d'Aurora -> de Confluence, qu'Aurora -> que Confluence
    text = re.sub(r"\b([dD])[’']Aurora(?![A-Za-z])", r"\1e Confluence", text)
    text = re.sub(r"\b([qQ])u[’']Aurora(?![A-Za-z])", r"\1ue Confluence", text)
    text = re.sub(r"\b([lL])[’']Aurora(?![A-Za-z])", r"\1a Confluence", text)
    text = WORD.sub("Confluence", text)
    for token, phrase in held.items():
        text = text.replace(token, phrase)
    return text


def rename_viewer_only(text):
    """In the demo's strings: the viewer's name only, never the places."""
    text = re.sub(r"\b([dD])[’']Aurora Viewer", r"\1e Confluence Viewer", text)
    return text.replace("Aurora Viewer", "Confluence Viewer").replace("Auroraビューア", "Confluenceビューア")


for path in sys.argv[1:]:
    overrides = next((v for k, v in OVERRIDES.items() if path.replace("\\", "/").endswith("/" + k) or path == k), {})
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = []
    key = None
    changed = 0
    for line in raw.split(nl):
        m = KEY.match(line)
        if m:
            key = m.group(1)
        if line.lstrip().startswith("#"):
            new = line
        elif m and key in overrides:
            new = line[: m.end()] + overrides[key]
        elif key and key.startswith(PROTECT_KEYS):
            new = rename_viewer_only(line)
        elif m:
            new = line[: m.end()] + rename(line[m.end():])
        else:
            new = rename(line)
        changed += new != line
        out.append(new)
    io.open(path, "w", encoding="utf-8", newline="").write(nl.join(out))
    print(path, "lines changed:", changed)
