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
- 2026-11-15: the bridge zip is dropped (no one is on 0.9.8); releases carry only the Confluence-Viewer packages.

## Voice buffer top-up for OpenSim (2026-11-15)

On Casperia Prime the network was clean (no loss, under 1 ms jitter), but the voice server stalls for 45-160 ms at
times. After a stall the playback queue sat at 20 ms for minutes, so every small delay broke up the speech.
`aurora-voice` now adds one Opus concealment frame when less than 30 ms is queued after a packet (as libwebrtc's NetEq
stretches its buffer); the voice stats line counts them as "topped up". **Not yet tested on the grid** (needs a second
person speaking). Possibly worth offering upstream once it is.

Merged 19 more upstream commits up to `47e5ccd5` (Aurora-Sim region settings, mouselook aids, name tag distance...).
No conflicts; no new Aurora text to rebrand. "Aurora-Sim" (grid software) only appears in code comments, so the rename
leaves it alone. One GPU test, `water_mesh_depth_clamp_preserves_coverage_and_occlusion_on_gpu`, fails on the RTX 3050
laptop (driver 621.24, software depth clamp path); the merge touched no water code.

## Releases v0.9.10-beta.20261116.1 and v0.9.10 (2026-11-16)

- Merged 31 upstream commits (the Director: a camera track and video recorder; films go to `Videos/Confluence Viewer`
  as `Confluence_<time>`), then tagged `v0.9.10-beta.20261116.1`: a pre-release, offered only to the Beta channel. It
  is the first release with a macOS build since the Mac packaging fix.
- Merged 20 more (Aurora's stable v0.9.10 is at `1c9c39c2`; our merge goes up to `59264a8e`) and tagged `v0.9.10`.
- First upstream PR from the fork: Aurora-Viewer/Aurora-Viewer#3859. The portable water depth clamp re-projected the
  interpolated world position, which an AMD Vulkan driver puts centimetres off near the camera, so
  `water_mesh_depth_clamp_preserves_coverage_and_occlusion_on_gpu` fails on this PC (wgpu tests use the AMD integrated
  GPU, the viewer the RTX 3050). The fix reads the fragment's own 1/w. Until it is merged upstream, that one test fails
  here; everything else passes.

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

## Merge up to Aurora 4bcf916f (2026-11-17)

- Merged 96 upstream commits (Aurora's v0.9.11 betas). Conflicts in the updater: Aurora's update now replaces only the
  package's own entries and keeps the user's files, and its install check asks for the viewer under the package name
  (`confluence-viewer.exe` here). So an install of 0.9.8 (viewer still named `aurora-viewer.exe`) no longer updates
  in place; v0.9.9 and later do (their packages carry `aurora-install.json`). The launcher under Aurora's old name is
  updated with the package (new test `the_launcher_under_aurora_name_is_updated_with_the_viewer`). 360° photos name
  Confluence Viewer as their software.
- PR #3859 rebased onto Aurora's main (TASKS.md conflict only), check.ps1 green, force-pushed; no review yet.
- HANDOFFS.md was lost and rebuilt by the OpenSim session. Its "Region ↔ viewer" interface now describes the Aurora
  fork, acknowledges OpenSim's Aurora Weather sky-mark row, and notes a gap: the viewer ignores the region's
  `stun-servers` and asks `stun1/2.<grid>.secondlife.io`, which do not exist off Second Life.

## Voice STUN servers and bug reports (2026-11-17)

- Voice off Second Life now uses the region's SimulatorFeatures `stun-servers` (as the Legacy Viewer does since
  FIRE-36421) instead of Linden's `stun*.agni.secondlife.io`. On Casperia that is `stun.l.google.com:19302` and
  `stun.cloudflare.com:3478` (live `OpenSim.ini` `StunServers`). Tested on the grid 2026-11-17: voice connects and
  sends; receiving from a remote user not yet tested. The voice log names the STUN servers used.
- Bug reports: Issues were off on the fork, so the browser path landed nowhere; turned on 2026-11-17. Direct sending
  and crash reports used Aurora's GitHub App (installed on Aurora's repo only); its client id is blanked, so the
  viewer says direct sending is not set up. **To do (owner):** register a Confluence GitHub App (Device Flow on,
  Issues read/write, installed on the fork) and put its Client ID in `bug_report/github.rs` and `crash/github.rs`.

## Release v0.9.11 (2026-11-18)

- Merged 54 upstream commits up to `52e6d985` (Aurora's stable v0.9.11: a complete Director, gaming mode, volumetric
  clouds, proxy settings, script sync with outside editors). The voice top-up now runs on Aurora's new playout path
  (gain ramp). Confluence names for the proxy password's store entry, the script-sync viewer name and the Director's
  image sequences; the Blender add-on's key folder keeps `Aurora\AuroraViewer` because the add-on reads it there.
- FFmpeg pack 1 (the Director's encoder) copied unchanged from Aurora's `ffmpeg-1` release to the fork's (checksums
  verified, source archive included for the GPL), since the viewer downloads packs from the fork's releases. Media
  plugin packs 1-3 on the fork already match Aurora's. **Each new Aurora pack release (media-plugins-N, ffmpeg-N)
  must be copied the same way before the merge that starts using it ships.**
- PR #3859 rebased again (TASKS.md), check.ps1 green, mergeable; still no review.

## Merge up to Aurora 231c88a3, region weather gone (2026-11-22)

- Merged 136 upstream commits (Aurora's stable v0.9.12 and v0.9.13 betas). **Region weather removed, as in Aurora**
  (#4280, Second Life's shared-experience policy): the viewer no longer reads OpenSimWeather 0.7.0's sky codes; the
  owner chose to follow Aurora. Confluence-OpenSim told (HANDOFFS row moved to Done, message sent).
- Updater: Aurora's in-place Linux updates, with Confluence names (`Confluence-Viewer-<tag>-linux-x64.tar.gz`,
  `confluence-viewer` executable on Linux). Release workflow: Aurora's optional SignPath signing comes along; it stays
  off on the fork (needs the `SIGNPATH_SIGN_RELEASES` variable).
- Twelve new interface languages. `rebrand-locales.py` now takes every catalogue (`locales/*.ftl`): English, French
  and Japanese phrase by phrase as before; the others follow English key by key, and the four keys that mix a kept
  feature name with the viewer's name are renamed name by name. Login tagline names OpenSim in all fifteen.

## Merge up to Aurora d10b1f68, repository repair (2026-11-22)

- Merged 29 upstream commits. Only the usual en/fr/ja locale conflicts; no new Aurora name users see in the code.
  check.ps1: all green but the known AMD water test (Aurora PR #3859, rebased on this main the same day).
- After the move from S: to G:, one pack of `.git` came out damaged (a blob of Aurora's `captures` branch,
  `pr-3669/shape-legacy.png`). Repaired by unpacking the pack's good objects, restoring that blob from GitHub
  (hash checked) and repacking; `git fsck` clean. The damaged pack is kept in `G:\Confluence-Viewer-badpack` until the
  owner deletes it.

## Other avatars no longer spin (2026-11-23)

- An Aurora user saw a Legacy Viewer user's avatar keep turning. Aurora extrapolated an avatar's reported angular
  velocity; the Legacy Viewer puts back another avatar's rotation after its motion step (LLVOAvatar::idleUpdate). OpenSim
  can leave its flying-roll yaw rate in an avatar's updates after landing. Fix: avatars ignore it (`Object::spin`,
  world/objects.rs), branch `fix/other-avatar-spin` from Aurora's main, cherry-picked here. Validated by the owner on
  the grid on 2026-11-23 (other avatars look normal); the spin itself did not reproduce again.
- The doubled outfits of the same evening came from Confluence-OpenSim's default-appearance fallback overwriting fresh
  bakes; OpenSim is fixing it.

## Merge up to Aurora e6978dcf (2026-11-23)

- Merged 24 upstream commits, no conflicts; locales rebranded, no new Aurora name users see. Aurora's release workflows
  now publish only when an admin starts them (`.github/actions/release-admin`): the owner is the fork's admin, so our
  releases are not affected. check.ps1 green but the known AMD water test (Aurora PR #3859).
- The avatar spin fix went to Aurora as PR #4635 (branch `fix/other-avatar-spin`).

## Release v0.9.13-beta.20261123.1 (2026-11-23)

- Tagged on main `94e14a76c` (Aurora up to e6978dcf, with the avatar spin fix): a pre-release for the Beta channel.
  The Release workflow built and published Windows, Linux and macOS.

## Merge up to Aurora 8e7cc561, signed updates arrive (2026-11-23)

- Merged 37 upstream commits. Our two Aurora PRs are merged there: #3859 (AMD water depth; the known AMD water test now
  passes, check.ps1 fully green) and #4635 (avatar spin). Their worktrees and branches are removed.
- **Signed updates (#4632):** the viewer installs only a release whose `.sha256` carries an Ed25519 signature by a key
  in `RELEASE_KEYS` (crates/aurora-updater/src/signature.rs); the publish jobs sign in the `release` environment
  (secret `UPDATE_SIGNING_KEY`), which allows main and stable tags only, so a beta is made from the Nightly workflow
  (Actions tab, on main), not by pushing a beta tag. Conflicts in release.yml and the updater tests resolved with
  Confluence package names; the Mac `.dmg` name in feed.rs rebranded; the fork-only launcher test restored.
- **Not set up yet:** `RELEASE_KEYS` still holds Aurora's key and the fork has no `release` environment, so the next
  release's publish jobs stop until the owner runs `scripts/setup-release-signing.ps1 -Repo Ramius1701/Confluence-Viewer`
  (it makes the key on the PC, stores it in the secret, never prints it, and adds the public half to RELEASE_KEYS);
  then Aurora's key line is removed and the change committed. Viewers already installed (0.9.13 beta and older) still
  trust the plain `.sha256` until their first update.
