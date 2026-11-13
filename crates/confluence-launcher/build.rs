//! The launcher shows the viewer's icon: shortcuts made to the old
//! `aurora-viewer.exe` take their picture from this file.

fn main() {
    #[cfg(windows)]
    {
        let manifest = std::env::var("CARGO_MANIFEST_DIR").expect("Cargo supplies CARGO_MANIFEST_DIR");
        let icon = std::path::Path::new(&manifest).join("../../assets/branding/confluence.ico");
        println!("cargo:rerun-if-changed={}", icon.display());
        let mut res = winresource::WindowsResource::new();
        res.set_icon(&icon.to_string_lossy())
            .set("ProductName", "Confluence Viewer")
            .set("FileDescription", "Confluence Viewer launcher")
            .set("OriginalFilename", "aurora-viewer.exe");
        if let Err(error) = res.compile() {
            panic!("Cannot embed the icon of the launcher (rc.exe of the Windows SDK): {error}");
        }
    }
}
