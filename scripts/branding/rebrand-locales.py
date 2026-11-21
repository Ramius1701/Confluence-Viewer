"""Renames the viewer in the Fluent locales, for Confluence Viewer.

Run it after every merge from Aurora Viewer's main branch, on every
catalogue (a merge conflict there is solved by taking upstream's file, then
running this again):

    python -I scripts/branding/rebrand-locales.py crates/aurora-i18n/locales/*.ftl

- "Aurora" becomes "Confluence" where the word names the viewer.
- Feature, place and preset names keep Aurora's: the offline demo world,
  photo looks, avatar parts, the in-world bridge, the "#Aurora" inventory
  folder the AO code reads, Aurora Weather, etc. In the demo's strings only
  the viewer's own name ("Aurora Viewer") changes.
- The login tagline says the viewer is for OpenSim as well as Second Life.
- English, French and Japanese are renamed phrase by phrase (below). The other
  languages follow English key by key: where the English value still says
  "Aurora" once renamed (a feature, place or preset), the translation keeps it
  too and only "Aurora Viewer" changes; elsewhere every "Aurora" becomes
  "Confluence". So en.ftl is renamed first, whatever the order given.

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
    # Aurora's own weather feature keeps its name
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
# The tagline in the other languages: "<client>  ·  Rust  ·  <API>".
TAGLINES = {
    "de.ftl": "Second Life- & OpenSim-Client",
    "es.ftl": "Cliente de Second Life y OpenSim",
    "it.ftl": "Client Second Life e OpenSim",
    "pl.ftl": "Klient Second Life i OpenSim",
    "tr.ftl": "Second Life ve OpenSim istemcisi",
    "pt-BR.ftl": "Cliente Second Life e OpenSim",
    "pt-PT.ftl": "Cliente Second Life e OpenSim",
    "nb.ftl": "Second Life- og OpenSim-klient",
    "uk.ftl": "Клієнт Second Life і OpenSim",
    "ru.ftl": "Клиент Second Life и OpenSim",
    "zh-Hans.ftl": "Second Life 与 OpenSim 客户端",
    "zh-Hant.ftl": "Second Life 與 OpenSim 用戶端",
}
for _name, _client in TAGLINES.items():
    OVERRIDES[_name] = {
        "ui-login-second-life-client-rust-vulkan": f"{_client}  ·  Rust  ·  Vulkan",
        "ui-login-second-life-client-rust-metal": f"{_client}  ·  Rust  ·  Metal",
    }
PHRASE_BY_PHRASE = ("en.ftl", "fr.ftl", "ja.ftl")
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


def rename_follow(text):
    """Another language, on a key whose English is fully renamed."""
    text = text.replace("aurora-viewer.exe", "confluence-viewer.exe")
    # Italian, Spanish and Portuguese elide like French
    text = re.sub(r"\b([dD])[’']Aurora(?![A-Za-z])", r"\1i Confluence", text)
    text = re.sub(r"(?<![A-Za-z])Auroras(?![A-Za-z])", "Confluences", text)  # de, nb genitive
    return WORD.sub("Confluence", text)


def base(path):
    return path.replace("\\", "/").rsplit("/", 1)[-1]


TOKEN = re.compile(r"(?<![A-Za-z])(?:Aurora|Confluence)(?![a-z])")


def values(path):
    """Each key's value, its lines joined (comments left out)."""
    out = {}
    key = None
    for line in io.open(path, encoding="utf-8").read().splitlines():
        m = KEY.match(line)
        if m:
            key = m.group(1)
            out[key] = line[m.end():]
        elif key and not line.lstrip().startswith("#"):
            out[key] += " " + line
    return out


def english_names(en_path):
    """Per key whose English value still says "Aurora" once renamed: the
    sequence of its names, True where English renamed it (a key that mixes
    a kept feature name with the viewer's name)."""
    names = {}
    for key, value in values(en_path).items():
        if "Aurora" in value:
            names[key] = [t == "Confluence" for t in TOKEN.findall(value)]
    return names


paths = sorted(sys.argv[1:], key=lambda p: base(p) != "en.ftl")
for path in paths:
    overrides = OVERRIDES.get(base(path), {})
    follow = base(path) not in PHRASE_BY_PHRASE
    kept = english_names(path[: len(path) - len(base(path))] + "en.ftl") if follow else {}
    # a mixed key is renamed name by name, as English does, when the
    # translation has as many names in the same places; otherwise kept
    counts = {k: len(TOKEN.findall(v)) for k, v in values(path).items()} if follow else {}
    seen = 0
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = []
    key = None
    changed = 0
    for line in raw.split(nl):
        m = KEY.match(line)
        if m:
            key = m.group(1)
            seen = 0
        if line.lstrip().startswith("#"):
            new = line
        elif m and key in overrides:
            new = line[: m.end()] + overrides[key]
        elif key and key.startswith(PROTECT_KEYS):
            new = rename_viewer_only(line)
        elif follow:
            head, body = (line[: m.end()], line[m.end():]) if m else ("", line)
            if key not in kept:
                body = rename_follow(body)
            elif any(kept[key]) and counts.get(key) == len(kept[key]):
                plan, start = kept[key], seen

                def swap(t, plan=plan, start=start, at=[0]):
                    i = start + at[0]
                    at[0] += 1
                    return "Confluence" if plan[i] else t.group(0)

                body = TOKEN.sub(swap, body)
                seen += len(TOKEN.findall(line[m.end():] if m else line))
            else:
                body = rename_viewer_only(body)
            new = head + body
        elif m:
            new = line[: m.end()] + rename(line[m.end():])
        else:
            new = rename(line)
        changed += new != line
        out.append(new)
    io.open(path, "w", encoding="utf-8", newline="").write(nl.join(out))
    print(path, "lines changed:", changed)
