//! Project links shown on the login screen. Empty = not configured yet: the
//! button is shown disabled and nothing is fetched. The README header carries
//! the same Discord and website links: change them there too.

/// Source code repository (GitHub page).
pub const GITHUB: &str = "https://github.com/Ramius1701/Confluence-Viewer";
/// Issue template chooser, opened in the browser by "Report a bug" (login
/// screen, top bar, Help menu) and by the crash window.
pub const NEW_ISSUE: &str = "https://github.com/Ramius1701/Confluence-Viewer/issues/new/choose";
/// The project's wiki, generated from the guides of `docs/`
/// (`scripts/build-wiki.ps1`): Help › wiki. Confluence Viewer has none of
/// its own yet, so this stays Aurora Viewer's, whose guides it follows.
pub const WIKI: &str = "https://github.com/Aurora-Viewer/Aurora-Viewer/wiki";
/// Community Discord invite.
/// Empty until Confluence Viewer has one (Aurora's was here).
pub const DISCORD: &str = "";
/// Project website.
/// Empty until Confluence Viewer has one (Aurora's was here).
pub const WEBSITE: &str = "";
/// The privacy policy on the website (Preferences › Privacy › Your data).
pub const PRIVACY_POLICY: &str = "https://aurora-viewer.org/privacy/";
/// News feed: this folder of `main`, hand-edited Markdown files, one
/// `<language>.md` per UI language (`news/` at the repository root). The
/// viewer keeps what it read in its cache as a JSON array of
/// `{"date", "title", "summary", "url"}`. Empty for now: `news/` still holds
/// Aurora Viewer's own news, which Confluence Viewer must not show as its own.
pub const NEWS_FEED: &str = "";
/// Files of the source repository as GitHub serves them unrendered; a branch
/// name and a path follow.
pub const RAW_FILES: &str = "https://raw.githubusercontent.com/Ramius1701/Confluence-Viewer/";
