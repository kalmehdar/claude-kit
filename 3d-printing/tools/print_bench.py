"""Build a Print Bench: one self-contained web page that shows every design in its print colours, with a rendered
picture of each in the list and a 3D viewer you can turn on a phone. Publish it as a Claude artifact or open it locally.

    python print_bench.py bench.json print-bench.html

bench.json (paths relative to it):
  {"title": "Print Bench", "sub": "intro line", "foot": "footer, HTML allowed", "bed": 256,
   "models": [{"id": "card", "name": "Test card", "for": "what it is for", "status": "Ready", "state": "ready",
               "material": "PETG, four heads", "credit": "Designed by ...",
               "parts": [["Red", "stl/test-card-red.stl", "#c8102e"], ...]}]}
state is "check" (fit it first), "ready" or "later". Set "nobed": true on a model too big to sit on the bed.
Grams are estimated from the shape (1 mm skin, 15% infill, PETG 1.27 g/cm3): about 20% either way; your slicer wins.
"""
import base64
import datetime
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def triangles(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:1000]:
        return [float(v) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data) for v in m]
    n = struct.unpack_from("<I", data, 80)[0]
    out = []
    for i in range(n):
        out.extend(struct.unpack_from("<9f", data, 84 + i * 50 + 12))
    return out


def grams(v, pla=False):
    vol = area = 0.0
    for i in range(0, len(v), 9):
        ax, ay, az, bx, by, bz, cx, cy, cz = v[i:i + 9]
        vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6
        ux, uy, uz, wx, wy, wz = bx - ax, by - ay, bz - az, cx - ax, cy - ay, cz - az
        area += ((uy * wz - uz * wy) ** 2 + (uz * wx - ux * wz) ** 2 + (ux * wy - uy * wx) ** 2) ** 0.5 / 2
    vol, skin = abs(vol), area * 1.0
    g = (min(vol, skin) + max(0.0, vol - skin) * 0.15) / 1000 * (1.24 if pla else 1.27)
    return round(g) if g >= 10 else round(g, 1)


def main():
    src, out = sys.argv[1], sys.argv[2]
    bench = json.load(open(src, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(src))
    models = []
    for m in bench["models"]:
        parts, allv = [], []
        for label, rel, colour in m["parts"]:
            v = triangles(os.path.join(base, rel))
            parts.append((label, colour, v, None if m.get("nobed") else grams(v, "PLA" in m.get("material", "") and "PETG" not in m.get("material", ""))))
            allv.extend(v)
        lo = [min(allv[a::3]) for a in range(3)]
        hi = [max(allv[a::3]) for a in range(3)]
        cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        packed = []
        for label, colour, v, g in parts:
            shifted = [v[i] - (cx, cy, lo[2])[i % 3] for i in range(len(v))]
            q0 = min(shifted) if shifted else 0.0          # 16-bit vertices: a quarter of the page size of floats
            step = max((max(shifted) - q0) / 65535, 1e-6) if shifted else 1.0
            ints = [round((x - q0) / step) for x in shifted]
            packed.append({"label": label, "colour": colour, "grams": g, "q0": q0, "qs": step,
                           "data": base64.b64encode(struct.pack(f"<{len(ints)}H", *ints)).decode()})
        models.append({"id": m["id"], "name": m["name"], "for": m.get("for", ""), "status": m.get("status", ""),
                       "state": m.get("state", "ready"), "material": m.get("material", ""), "credit": m.get("credit", ""),
                       "nobed": m.get("nobed", False), "size": [round(hi[a] - lo[a], 1) for a in range(3)],
                       "parts": packed, "sliced": []})
        print(f"{m['name']}: {models[-1]['size']} mm, {len(allv) // 9} triangles")
    config = {k: bench[k] for k in ("title", "sub", "foot", "mark", "markLang", "bed") if k in bench}
    tpl = open(os.path.join(HERE, "print-bench-template.html"), encoding="utf-8").read()
    html = (tpl.replace("/*MODELS*/[]", json.dumps(models, separators=(",", ":")))
            .replace("/*CONFIG*/{}", json.dumps(config, ensure_ascii=False))
            .replace("/*TITLE*/", bench.get("title", "Print Bench"))
            .replace("/*BUILT*/", datetime.datetime.now().strftime("%d %b %Y")))
    open(out, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main()
