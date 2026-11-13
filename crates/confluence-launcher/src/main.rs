//! `aurora-viewer.exe` of a Confluence Viewer package for Windows.
//!
//! The viewer was `aurora-viewer.exe` until Confluence Viewer 0.9.8; it is
//! `confluence-viewer.exe` since. Shortcuts, pinned taskbar icons and
//! `secondlife://` handlers made before the rename still point at the old
//! name: this launcher, packaged under it (`scripts/package.ps1`), starts the
//! viewer next to it with the same arguments and working folder, then exits.
//! It does not wait: the viewer is the process the user sees.

#![cfg_attr(windows, windows_subsystem = "windows")]

use std::process::{Command, ExitCode};

/// The viewer this launcher starts, in the launcher's own folder.
const VIEWER: &str = if cfg!(windows) {
    "confluence-viewer.exe"
} else {
    "confluence-viewer"
};

fn main() -> ExitCode {
    let viewer = match std::env::current_exe() {
        Ok(exe) => exe.with_file_name(VIEWER),
        Err(error) => {
            eprintln!("confluence-launcher: cannot locate itself: {error}");
            return ExitCode::FAILURE;
        }
    };
    match Command::new(&viewer).args(std::env::args_os().skip(1)).spawn() {
        Ok(_) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("confluence-launcher: cannot start {}: {error}", viewer.display());
            ExitCode::FAILURE
        }
    }
}
