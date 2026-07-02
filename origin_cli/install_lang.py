import subprocess

LANG_MAP = {
    "python": "Python.Python",
    "node": "OpenJS.NodeJS",
    "nodejs": "OpenJS.NodeJS",
    "js": "OpenJS.NodeJS",
    "javascript": "OpenJS.NodeJS",
    "java": "Eclipse.Temurin.21.JDK",
    "jdk": "Eclipse.Temurin.21.JDK",
    "git": "Git.Git",
    "go": "GoLang.Go",
    "golang": "GoLang.Go",
    "dotnet": "Microsoft.DotNet.SDK.8",
    "dotnetcore": "Microsoft.DotNet.SDK.8",
    "rust": "Rustlang.Rustup",
    "rustup": "Rustlang.Rustup",
    "ruby": "RubyInstaller.Ruby",
    "php": "PHP.PHP",
    "cmake": "Kitware.CMake",
    "make": "GnuWin32.Make",
    "gcc": "GnuWin32.GCC",
    "mingw": "MSYS2.MSYS2",
    "vscode": "Microsoft.VisualStudioCode",
    "code": "Microsoft.VisualStudioCode",
    "docker": "Docker.DockerDesktop",
    "nginx": "NGINX.NGINX",
    "postgresql": "PostgreSQL.PostgreSQL",
    "postgres": "PostgreSQL.PostgreSQL",
    "redis": "Redis.Redis",
    "sqlite": "SQLite.SQLite",
    "curl": "cURL.cURL",
    "wget": "GNU.WGet",
    "7zip": "7zip.7zip",
    "ffmpeg": "FFmpeg.FFmpeg",
    "vlc": "VideoLAN.VLC",
    "firefox": "Mozilla.Firefox",
    "chrome": "Google.Chrome",
    "powertoys": "Microsoft.PowerToys",
}

def _winget_cmd(action: str, pkg_id: str) -> int:
    try:
        result = subprocess.run(
            ["winget", action, "--id", pkg_id, "--accept-source-agreements", "--accept-package-agreements"],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        print("winget is not installed or not in PATH. Install it from https://aka.ms/getwinget")
        return 1
    if result.returncode != 0:
        print(f"winget {action} failed: {result.stderr.strip() or result.stdout.strip()}")
    else:
        print(result.stdout.strip())
    return result.returncode

def _map_lang(lang: str) -> str | None:
    key = lang.strip().lower()
    pkg = LANG_MAP.get(key)
    if not pkg:
        print(f"Unknown language/tool: '{lang}'. Try using the winget ID directly.")
    return pkg

def install_lang(lang: str) -> None:
    pkg = _map_lang(lang)
    if pkg:
        _winget_cmd("install", pkg)

def uninstall_lang(lang: str) -> None:
    pkg = _map_lang(lang)
    if pkg:
        _winget_cmd("uninstall", pkg)
