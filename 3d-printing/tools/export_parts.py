"""Export every colour part of an OpenSCAD model to its own STL, and check each fits the printer bed.

    python export_parts.py model.scad [--out stl/] [--bed 256x256x256]

Parts come from a `// parts: a b c` line in the model, else its `part == "..."` lines ("all" is preview only). Each goes to
<out>/<model>-<part>.stl as binary STL; a model with no parts goes to <out>/<model>.stl.
OpenSCAD: the OPENSCAD environment variable, else `openscad` on PATH, else the usual Windows install.
A 2025+ OpenSCAD snapshot is much faster: it renders with the manifold backend, used when available.
"""
import argparse
import os
import re
import shutil
import struct
import subprocess
import sys

PREVIEW_ONLY = {"all", "both"}


def openscad():
    for c in (os.environ.get("OPENSCAD"), shutil.which("openscad"), r"C:\Program Files\OpenSCAD\openscad.com"):
        if c and os.path.exists(c):
            return c
    sys.exit("OpenSCAD not found. Install it from openscad.org (a nightly snapshot is fastest), or set OPENSCAD.")


def parts_of(text):
    """A `// parts: a b c` line wins; otherwise every literal `part == "name"` in the model."""
    m = re.search(r"^//\s*parts:\s*(.+)$", text, re.M)
    found = m.group(1).split() if m else re.findall(r'part\s*==\s*"(\w+)"', text)
    return [n for i, n in enumerate(found) if n not in PREVIEW_ONLY and n not in found[:i]]


def size_of(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:1000]:
        pts = [tuple(map(float, m)) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
    else:
        n = struct.unpack_from("<I", data, 80)[0]
        pts = [struct.unpack_from("<3f", data, 84 + i * 50 + 12 + v * 12) for i in range(n) for v in range(3)]
    return tuple(max(p[a] for p in pts) - min(p[a] for p in pts) for a in range(3)) if pts else (0, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--out", default="stl")
    ap.add_argument("--parts", help="comma-separated part names, overriding the model")
    ap.add_argument("--bed", default="256x256x256", help="build volume in mm, WxDxH")
    a = ap.parse_args()
    bed = tuple(float(x) for x in a.bed.lower().split("x"))
    tool = openscad()
    helptext = subprocess.run([tool, "--help"], capture_output=True, text=True)
    fast = ["--backend=manifold"] if "manifold" in (helptext.stdout + helptext.stderr) else []
    conf = os.path.join(os.path.dirname(tool), "fonts", "10-liberation.conf")   # snapshots ship their own fonts
    if os.path.exists(conf):
        os.environ.setdefault("FONTCONFIG_FILE", conf)
    name = os.path.splitext(os.path.basename(a.model))[0]
    os.makedirs(a.out, exist_ok=True)
    parts = a.parts.split(",") if a.parts else parts_of(open(a.model, encoding="utf-8").read())
    targets = [(p, os.path.join(a.out, f"{name}-{p}.stl")) for p in parts] or [(None, os.path.join(a.out, f"{name}.stl"))]
    ok = True
    for part, out in targets:
        cmd = [tool] + fast + ["--export-format", "binstl", "-o", out, a.model] + (["-D", f'part="{part}"'] if part else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not os.path.exists(out):
            print(f"FAIL  {part or name}: OpenSCAD error\n{r.stderr.strip()[-600:]}")
            ok = False
            continue
        s = size_of(out)
        fit = all(x <= b for x, b in zip(sorted(s), sorted(bed)))
        ok = ok and fit
        print(f"{'ok  ' if fit else 'FAIL'}  {out}  {s[0]:.1f} x {s[1]:.1f} x {s[2]:.1f} mm  {'fits' if fit else 'TOO BIG for the bed'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
