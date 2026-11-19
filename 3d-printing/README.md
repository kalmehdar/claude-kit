# 3D printing with Claude Code

How I design and check prints with Claude: describe the part, Claude writes it in OpenSCAD with every size as a named number, the tools export one STL per colour, a mesh check catches what a slicer would choke on, and a Print Bench page shows every design in its real colours before a gram of filament is used.

Live example: [Print Bench demo](https://claude.ai/code/artifact/473d4b53-a14b-4b78-b0e5-df214c37158f), built from `examples/`.

## What's here

| Path | What it does |
| --- | --- |
| `tools/export_parts.py` | Exports each colour part of an OpenSCAD model to its own STL and checks it fits your bed |
| `tools/mesh_audit.py` | Runs inside Blender: non-manifold edges, inside-out meshes, pieces, thin walls, bed fit |
| `tools/print_bench.py` | Builds the Print Bench page from a `bench.json` (one HTML file, works offline, fine on a phone) |
| `examples/models/` | Three designs: a four-colour test card, colour-coded Gridfinity bins, clip-on cable tags sized per cable |
| `examples/stl/`, `examples/bench.json` | Their exported parts and the demo page's list |

The 3D skills and agents are in the kit's `skills/` and `agents/3d/`: `3d-print-designer` (FDM design rules, materials, verification), plus `modeling`, `blender`, `blender-3d-modeling`, `texturing`, `asset-optimization`, `animation`, `rigging` and more.

## Set up

1. Install [OpenSCAD](https://openscad.org/downloads.html). Take a development snapshot: it renders with the manifold backend, seconds instead of minutes.
2. Install [Blender](https://www.blender.org/download/) for the mesh check (optional, but it catches problems early).
3. Install your printer maker's slicer (Bambu Studio, OrcaSlicer, PrusaSlicer, Snapmaker Orca).
4. Copy the kit's skills as the main README says, so Claude has `3d-print-designer`.

## Try it

```bash
cd 3d-printing/examples
python ../tools/export_parts.py models/test-card.scad --out stl --bed 256x256x256
blender --background --factory-startup --python ../tools/mesh_audit.py -- stl --bed 256
python ../tools/print_bench.py bench.json print-bench.html
```

Open `print-bench.html` in a browser. To share it, ask Claude to publish it as an artifact.

Set `OPENSCAD` to the binary if it isn't on your PATH. A model lists its colour parts on its first line (`// parts: red blue white black`); each becomes `<model>-<part>.stl`. In the slicer, load all of a model's parts as one object and give each part its own head.

## The way I work with Claude

- Ask for a part with its job and its numbers. "A bin for 10 USB sticks, 42 mm Gridfinity grid, label USB printed into the front."
- Never let Claude guess a fit size. Anything that clips onto, slides into or screws to something real needs a caliper number. Claude marks those `FIT` and you measure before printing.
- Labels are printed in, not stuck on. A 0.6 mm pocket in the body, the letters in a second colour filling it, printed face down.
- One colour per head, one STL per colour. The `part` variable picks which colour a run of OpenSCAD draws.
- Check before slicing. `mesh_audit.py` must say 0 files need a fix. Squares that touch only at a corner are the usual non-manifold culprit; overlap them by 0.01 mm.
- Look at it first. Rebuild the Print Bench and turn the model round on your phone before you print.

## First-week tips

From DIY WISCO's [10 Things I Wish I Knew Before I Started 3D Printing](https://youtu.be/fetbc62jeWI), in my words, plus what four colours taught us:

- Start with PLA. PETG when it needs to take heat; ABS and ASA want an enclosure and real ventilation.
- Use the slicer's own profiles. The maker's slicer, your printer, your filament, default settings, until a few prints succeed.
- A print that won't stick usually means a dirty plate. Wash it with dish soap and warm water, dry it fully, hold it by the edges. Glue stick if that fails.
- Watch the first layer, then walk away. Even lines that are stuck down mean the rest will probably go fine. Check on it by camera if you have one.
- Dry your filament. Popping at the nozzle, sudden stringing or a rough surface mean wet filament. PETG soaks it up faster than PLA, and new sealed spools can still be wet.
- Supports only where needed. Tree supports come off more easily.
- The time estimate is a guide. Expect it to run over.
- For models, try MakerWorld, Printables, Thingiverse. Pick ones with photos of real prints.
- For several colours, print the test card first. A four-colour plate needs room for the prime tower, so a set that fills the bed splits into two plates.
