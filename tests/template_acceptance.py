#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True, check=True)


def executable(path: Path) -> bool:
    return bool(path.stat().st_mode & stat.S_IXUSR)


def main() -> None:
    wiring = json.loads((ROOT / "WIRING.json").read_text(encoding="utf-8"))
    assert wiring, "empty wiring"
    assert (ROOT / "template" / "_components").exists()
    for rel, info in wiring.items():
        path = ROOT / "template" / rel
        assert path.is_symlink(), f"not a symlink: {rel}"
        resolved = path.resolve(strict=True)
        assert "_components" in resolved.parts, f"outside submodule: {rel}"
        assert executable(resolved) == bool(info["executable"]), rel

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "generated"
        run("copier", "copy", "--defaults", "--vcs-ref", "HEAD", str(ROOT), str(out))
        assert (out / ".copier-answers.yml").is_file()
        assert not (out / "_components").exists()
        assert not (out / "template" / "_components").exists()
        for file in out.rglob("*"):
            if not file.is_file():
                continue
            try:
                text = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            assert not ("<<<<<<< " in text and "\n=======\n" in text and "\n>>>>>>> " in text), file

        # A component-owned executable must remain executable after dereferencing.
        executable_outputs = [rel for rel, info in wiring.items() if info["executable"]]
        if executable_outputs and os.name != "nt":
            assert executable(out / executable_outputs[0]), executable_outputs[0]

        result = {
            "repository": ROOT.name,
            "wiring_files": len(wiring),
            "rendered_files": sum(1 for p in out.rglob("*") if p.is_file()),
            "platform": os.name,
        }
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
