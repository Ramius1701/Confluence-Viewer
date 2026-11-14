# Confluence-Viewer project log

The durable record for the Confluence viewer. Nothing is built yet. The first plan (2026-10-18) is in
Confluence-OpenSim's PROJECT_LOG under "WolfViewer added as a viewer donor" and "Combined viewer". From here on, viewer
notes go in this file. Cross-project requests go in `S:\Github\Confluence-Shared\HANDOFFS.md`.

## Where the plan stands (2026-10-18, on hold at the plan stage)

- Base: Firestorm master, built with `-DOPENSIM:BOOL=ON`, is the authority. Features are ported one at a time from the
  donors, which are never merged whole. Donor file prefixes (`as*`, `wolf*`) are kept so the origin of the code stays
  clear.
- Order: (1) WolfViewer's general fixes (OpenSim WebRTC empty ICE list, varregion load and flicker, neighbour and
  teleport crashes, teleport retry, security fixes); (2) AyaneStorm, close to whole; (3) WolfViewer features that run
  in the viewer alone; (4) WolfViewer features tied to Wolf's web services: rebuild against Confluence, or drop.
- One sky stack: AyaneStorm's, because it stays on EEP, and Confluence's weather reaches the viewer as a per-avatar EEP
  override over `ExtEnvironment` (an agreed interface, see HANDOFFS).
- Stays multi-grid; no Wolf lock-in, branding or updater.

Viewer donor clones (all in `S:\Github`, partial clones): `phoenix-firestorm`, `ayanestorm`, `wolfviewer` (branch
`wolfviewer`), `secondlife-viewer`, CoolVL, and `Aurora-Viewer` (below).

## Aurora Viewer surveyed (2026-11-08)

`S:\Github\Aurora-Viewer` (Aurora-Viewer/Aurora-Viewer, `main` at `fc75f9a1`, 2026-11-07; release
`v0.9.4-beta.20261107.1`).

- **What it is:** a new viewer written from scratch in **Rust**, with a Vulkan renderer and a redesigned interface
  (each redesigned window can be switched back to the legacy look). It is not a Firestorm fork. Its 13 crates hold
  about 900k lines. Licence **GPLv3**; code it takes from the SL viewer and Firestorm is relicensed under LGPL 2.1 s.3
  (NOTICE.md).
- **Pace:** the first commit was 2026-10-08, and it has 1,438 commits in a month. It is built mostly by AI agents
  (AGENTS.md, HUMANS.md, CLAUDE.md), with humans choosing tasks and testing on the grid. Main authors by commit count:
  Ødesså Drækåvik (858) and Rohacan Hirons (340).
- **OpenSim:** real and recent. It has a grid manager (`get_grid_info`) and Hypergrid (`hop://`,
  `x-grid-location-info://`, gatekeeper:region teleports, My Suitcase). It works without AIS: inventory by
  FetchInventoryDescendents2 plus UDP edits, wearable and script saves, and profiles over UDP. It does its own bakes
  where the region doesn't bake, and handles large regions (heightmap, parcel overlay, positions). People tested this on
  OpenSim grids on 2026-11-02 and 11-03. It reads the usual `OpenSimExtras` keys (`map-server-url`,
  `search-server-url`, `GridURL`, chat ranges, prim scales, `currency-base-uri`, `ExportSupported`, `GridStatus`),
  `ExtEnvironment` and `VoiceServerType`. Still open per its TASKS.md: legacy Windlight for regions without EEP,
  OpenSim `[WL]` skies, several large-region edge cases, and thumbnails and material imports (need AIS).
- **Voice:** WebRTC only, no Vivox. **It does not read `stun-servers` from SimulatorFeatures yet**: the field exists
  (`aurora-voice/src/lib.rs:76`) but nothing sets it, so on OpenSim it uses Second Life's STUN servers
  (`stun{1,2}.agni.secondlife.io`). That probably still works, but it is not what Confluence sends. It is worth
  reporting to Aurora once someone tests it with Confluence-Voice.
- **What it means for the plan:**
  - Code can't move between Aurora and the Firestorm-based viewer: Rust versus C++, and GPLv3 can't go into an LGPL
    viewer without making the whole viewer GPLv3.
  - Ideas and protocol findings can move: its OpenSim notes cite the exact Firestorm and OpenSim sources, so they are a
    good checklist.
  - The real question it raises is strategic: build a Confluence viewer at all, or make Confluence work well with
    Aurora (and stock Firestorm) and contribute upstream. Aurora is a month old and still beta, moving fast, and
    agent-maintained; how well it ages is unknown.

## Direction: leaning towards Aurora (2026-11-08)

The owner leans towards Aurora for Confluence-Viewer, with Firestorm and Aurora both contenders. The reasoning: Aurora
is being built from scratch, so OpenSim gaps show up early and one at a time, each written down with the Firestorm and
OpenSim source it was checked against. Finding the same things in Firestorm means searching a very large codebase.
Example: Aurora ignores the access-255 block that OpenSim's `MapSearchModule.AddFinalBlock` appends to a map name search
(`aurora-net/src/session.rs:4855`, named teleports only).

Not decided: whether Confluence-Viewer would be a fork of Aurora, or Confluence works with upstream Aurora and sends
fixes there (GPLv3 either way). The combined Firestorm plan above stays on file. The first step either way is for the
owner to log in to Casperia with Aurora and see what breaks. Known so far: it doesn't read `stun-servers`.

## Aurora in daily use (2026-11-08)

The owner has used Aurora for two days and is impressed so far. Not yet reported: voice, the weather sky, large regions,
Hypergrid and Map Find on Casperia specifically.

## First Casperia finding: grid status is empty (2026-11-08)

Aurora's Grid status window says "This grid does not publish its status", and Firestorm never showed it either. This is
not a viewer bug. Both read `GridStatus` / `GridStatusRSS` from `OpenSimExtras`. Robust forwards them from
`[GridInfoService]`, but live `Robust.HG.ini` has them commented out. Handed to OpenSim (HANDOFFS row 2026-11-08): set
`GridStatus` to the portal's `/gridstatus`, and optionally add a real Atom/RSS feed. With only the page, Aurora shows an
"Open the status page" button; with a feed it lists incidents itself.

## Aurora on Casperia: Hypergrid and varregions work (2026-11-08)

The owner reports that Hypergrid travel and varregions work as usual in Aurora on Casperia. Still untested there:
voice (Aurora uses Second Life's STUN servers, not `stun-servers`), the weather sky, and Map Find on your own region.

Map Find is not a useful test in Aurora. Its map keeps the search results (`WorldMap::search`, filtered from the known
regions) apart from the tracked spot. Arriving within 3 m (`check_arrival`, ported from LLTracker) clears only the
track, so the result list never disappears the way it does in Firestorm. The Casperia Map Find bug stays a
Firestorm-path investigation for Confluence-OpenSim.

## Grid status: OpenSim's side done, feed checked (2026-11-08)

OpenSim set `GridStatus = ${Const|BaseURL}/gridstatus` in live `Robust.HG.ini` (with the owner's OK). It takes effect at
the next Robust restart plus a rolling region restart. It also built an Atom feed at `/gridstatus/feed`
(Confluence-OpenSim `b4209f6fa5`, not yet deployed; the `GridStatusRSS` line is waiting on the owner). Checked against
Aurora's parser: it displays. But with a plain-text `summary`, every entry shows as a neutral "Notice". Aurora's
incident and resolved badges need status-page HTML (`<small>when</small><br><strong>Investigating|Resolved|…</strong> -
text`, newest first) in `<content type="html">`. An outage should also be one entry whose `updated` changes when it
resolves. Sent to OpenSim as a suggestion. In-viewer check: Confluence-OpenSim TESTING 8.10.
Follow-up the same day: OpenSim adopted the status-page form in `2b710e120b` (pushed; DLL deployed, live at the next
Robust restart). Checked against Aurora's parser: it matches. Outages are one entry, Investigating then Resolved;
notices have no status. Only the live `GridStatusRSS` line is left, for the owner.
Later the same day: the owner reports the Grid status window now works on Casperia.

## Forked: Confluence-Viewer is a fork of Aurora (2026-11-08)

The owner decided to fork Aurora. `github.com/Ramius1701/Confluence-Viewer` is a GitHub fork of Aurora-Viewer, cloned
into this folder (`origin` = the fork, `upstream` = Aurora-Viewer), `main` at `29dd6a4c` (2026-11-08). The Firestorm
plan above is superseded; it stays on file.

- **Rules from Aurora's TRADEMARKS.md and GPLv3:** a modified version needs its own name and icon (no Aurora name or
  wolf logo as its brand), keeps Aurora's copyright and licence notices including the About window, and says it was
  modified and when. Calling it "based on Aurora Viewer" is fine.
- **Keep it a thin fork.** Upstream lands dozens of commits a day, so merging `upstream/main` must stay cheap. Rename
  only what users see (app name, window title, installer, icons, About window, data folder), and leave the
  `aurora-*` crate names and internal identifiers alone. Send OpenSim fixes upstream as PRs where they are general.
- **To do before any build is shared:** the rebrand above; point `aurora-updater` away from Aurora's releases (or
  disable it), so it can't replace our build with theirs; a Confluence icon (the owner supplies it).
- **First Confluence change:** read `stun-servers` from SimulatorFeatures (`aurora-voice/src/lib.rs:76`), a good
  upstream PR too.

## Rebrand to Confluence Viewer (2026-11-08)

First Confluence change on the fork, not committed yet. A thin rebrand: what users see is renamed, while crate names,
`AURORA_*` variables and internal identifiers stay Aurora's so `upstream/main` keeps merging cleanly.

- **Logo:** new, drawn by `scripts/branding/make-logo.py`: two streams, violet and teal, that meet and run on together
  inside a ring (a confluence). It writes `assets/branding/confluence-logo{,-white,-black}.svg`, `confluence-logo.png`,
  `confluence.ico` and `confluence.icns`. The build, the window icon, the top-bar brand icon (key still `"wolf"`),
  and the Windows and macOS packages use them. Aurora's logo files stay in the tree, unused.
- **Name:** "Confluence Viewer" in the Windows resource, login and loading screens, About, crash window, notifications,
  link handler, macOS plist, Linux desktop entry, and the en/fr/ja locales. Feature and place names stay Aurora's (the
  offline demo world, "#Aurora" inventory folder, Aurora bridge, Aurora AO, photo looks, avatar parts).
- **Grid-visible:** login channel `Confluence Viewer`, user agent `ConfluenceViewer/<version>`.
- **Separate from an Aurora install:** data folders `org/Confluence/ConfluenceViewer`, credential-store service names,
  Windows notification id `Confluence.Viewer`.
- **Repointed to the fork:** updater feed, release page and downloads (so Aurora's `aurora-update-policy.json` can't
  force or block us), crash and bug reports, the GitHub link. Website, Discord and the news feed are empty until
  Confluence has its own; the Help wiki stays Aurora's.
- **GPLv3 / TRADEMARKS.md:** NOTICE.md (shown in About › Licences) gains a "modified version of Aurora Viewer" section
  dated 2026-11-08; README gets a Confluence header saying the same.
- **Left for later:** the executable is still `aurora-viewer.exe`; release asset names are still
  `Aurora-Viewer-<tag>-*.zip` (updater and scripts agree); `PRIVACY_POLICY` still points at aurora-viewer.org.
- **Checked:** `cargo test --workspace`. Four tests that pinned Aurora's names were updated, and pass. Two GPU pixel tests
  in `aurora-render` (`water_mesh_depth_clamp…`, `pbr_terrain_samples…`) fail on this PC. The rebrand doesn't touch
  that crate, but they weren't run on an unmodified checkout to compare. `cargo fmt --check` passes. Clippy and
  `check.ps1` weren't run, and the viewer wasn't launched.

## Media plugins hosted on the fork (2026-11-08)

The first launch after the rebrand (b3e431bd) ran and closed cleanly, and logged as Confluence Viewer. It found one
break: the 240 MB media plugins pack (CEF, VLC, SLPlugin) downloads from the release feed, which now points at the
fork. The fork had no releases, so the download got a 404 and web pages and video had no plugins.

Fixed by copying Aurora's `media-plugins-1`, `-2` and `-3` releases to the fork unchanged. That covers Windows (all
three), Linux (2, 3) and macOS (3), with their `.sha256` files and the LGPL source archives. Each archive's SHA-256 was
checked against Aurora's before upload. The archives keep Aurora's names (`Aurora-Media-Plugins-<n>-<system>.zip`),
because the viewer builds the name and checks size and hash itself (`aurora-updater/src/media_pack.rs`). When upstream
moves to a new pack, copy that release too, or media breaks again.

## Upstream sync (2026-11-12)

Merged 173 commits from Aurora's `main` (up to cf5445ce, release v0.9.7-beta.20261111.2). Only the three locale files
conflicted: they were taken from upstream and renamed again with the same Aurora → Confluence script. A new data folder
in `blender_live/installer.rs` was moved to the Confluence one. The media plugins pack is unchanged (still 1–3), so
nothing new needs copying. The outfit HD picture keeps Aurora's inventory marker
(`Outfit HD picture (Aurora Viewer)`), so outfits stay compatible with Aurora users. Tests: everything passes
except the same two GPU tests in `aurora-render` that already failed on this PC.
- 2026-11-12, later: merged 3 more upstream commits (up to b564c18e: script recovery after a crash, the reorganized
  Build window, the 0.9.7 README notes). Locales renamed again; tests as above.

## More renaming, and OpenSim in the tagline (2026-11-12)

Merged 4 more upstream commits (startup splash, voice ICE fix, complexity notice, AMD leaves/hair). Renamed what
still said Aurora Viewer: the new startup splash title, the login screen's account carousel title, the photo folder
(`Pictures\Confluence Viewer`), the media browser's user agent, the Linux media audio stream names, and the demo's
mentions of the viewer (places in the demo world keep their Aurora names). The login tagline now reads
"Second Life & OpenSim client · Rust · Vulkan" (French and Japanese too).

The locale rename now lives in the repo, `scripts/branding/rebrand-locales.py`: after each upstream merge, take
upstream's three `.ftl` files on conflict and run it on them. It is idempotent.

## First Confluence release, v0.9.8 (2026-11-13)

Merged 24 more upstream commits (Aurora's 0.9.8 and the first 0.9.9 betas). The fork had been running Aurora's
Nightly workflow twice a day; every run failed at `scripts/verify-version.ps1`, which expected the exe to say
"Aurora Viewer", and left three `v0.9.4-beta…` tags on GitHub (20261108.2, 20261109.1, 20261112.1, deleted). Fixed
for the fork:

- `verify-version.ps1` expects "Confluence Viewer <version>"; the release title is "Confluence Viewer <tag>".
- `.github/release-notes-header.md` names Confluence, credits Aurora Viewer, and points support at the fork's issues.
- The Nightly schedule is off: releases are made by hand (a version tag), or a beta from the Actions tab.
- Version numbers follow the Aurora release a Confluence release is built on (v0.9.8 here). The local clone no
  longer fetches Aurora's tags (`remote.upstream.tagOpt --no-tags`), so `git describe` only sees the fork's.

The release asset names stay Aurora's (`Aurora-Viewer-<tag>-windows-x64.zip`): the updater looks for that name.

## Program and downloads renamed to Confluence (2026-11-13)

Merged 14 more upstream commits (Aurora fixed the same clippy 1.100 loops; their versions are kept). Then renamed what
users download and run:

- Releases are `Confluence-Viewer-<tag>-windows-x64.zip` (also `-linux-x64.tar.gz`, `-macos-arm64.dmg`, and the
  Windows symbols zip). The program inside is `confluence-viewer.exe` (`confluence-viewer` on Linux).
- Cargo still builds `aurora-viewer(.exe)`: `scripts/package.ps1` renames it in the package (`-ExeName`). This keeps
  CI, scripts and docs merging cleanly from Aurora.
- The Windows package also ships `aurora-viewer.exe`, a tiny launcher (`crates/confluence-launcher`) that starts
  `confluence-viewer.exe`, so old shortcuts, pinned icons and `secondlife://` handlers keep working.
- **Bridge for 0.9.8 installs:** their updater only finds `Aurora-Viewer-<tag>-windows-x64.zip` and refuses a package
  with files it doesn't know. Each release also carries that zip, holding the viewer itself as `aurora-viewer.exe`.
  The new updater accepts an install under either name (`install::LEGACY_EXE`) and moves it to the new package on the
  next update. Drop the bridge zip once no one is on 0.9.8 (a few releases).
- Kept on purpose: `aurora-update-policy.json` (0.9.8's updater reads that name), the Linux desktop id
  `aurora-viewer` (window matching), the macOS bundle's inner executable, and Aurora's media plugin pack names.
- 2026-11-15: merged 39 more upstream commits (Aurora Weather, 1024 m draw distance, Collada/OBJ export, SLua editor).
  `install.rs` kept both sides (our exe names, upstream's drive-root check). "Aurora Weather" keeps its name in every
  language: regions set it for all viewers, like "Aurora water" (protected in `rebrand-locales.py`). Exported models
  name Confluence Viewer as their authoring tool.
