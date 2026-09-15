"""Build an unpackable desktop folder; build on each target operating system."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    from adaptive_chess.experiments.campaign import environment_metadata

    build = ROOT / "build" / "desktop"
    build.mkdir(parents=True, exist_ok=True)
    manifest = build / "_build.json"
    manifest.write_text(json.dumps(environment_metadata(), indent=2), encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--name",
        "AdaptiveChessAI",
        "--onedir",
        "--console",
        "--paths",
        str(ROOT / "src"),
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(build / "work"),
        "--specpath",
        str(build),
        "--add-data",
        f"{ROOT / 'scripts'}:scripts",
        "--add-data",
        f"{manifest}:adaptive_chess",
        "--collect-submodules",
        "adaptive_chess",
        "--hidden-import",
        "matplotlib.backends.backend_agg",
    ]
    for name in ("chess", "PySide6", "pandas", "matplotlib"):
        command.extend(["--copy-metadata", name])
    if sys.platform == "win32":
        command.extend(["--hide-console", "hide-early"])
    command.append(str(ROOT / "src" / "adaptive_chess" / "__main__.py"))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    if sys.platform == "win32":
        # Unrelated PATH tools can contain incompatible DLLs (e.g. Poppler ICU).
        windows = Path(os.environ["SYSTEMROOT"])
        environment["PATH"] = os.pathsep.join(
            map(
                str,
                [
                    Path(sys.executable).parent,
                    Path(sys.base_prefix),
                    windows / "System32",
                    windows,
                ],
            )
        )
    subprocess.run(command, cwd=ROOT, env=environment, check=True)


if __name__ == "__main__":
    main()
