"""Check every STL in a folder for the faults that make a slicer choke, before you print.

    blender --background --factory-startup --python mesh_audit.py -- stl/ [--bed 256]

Per file: triangles, non-manifold edges, separate pieces, area thinner than 0.8 mm (two 0.4 mm lines), inside out
(negative volume) and size against the bed. Only non-manifold, inside out and too big are faults (exit code 1).
Pieces: a single solid part should be 1; lettering and print sheets are many by design. Thin area: label pockets and
chamfers count too, so a big number on a solid part means look at that spot in the slicer preview.
"""
import bpy, bmesh, os, sys
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["stl"]
folder = args[0]
BED = float(args[args.index("--bed") + 1]) if "--bed" in args else 256.0
MIN_WALL = 0.8
bad = 0
print(f"{'file':<44}{'tris':>8}{'nonman':>8}{'pieces':>7}{'thin mm2':>10}  size / verdict")
for name in sorted(f for f in os.listdir(folder) if f.lower().endswith(".stl")):
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
    bpy.ops.wm.stl_import(filepath=os.path.join(folder, name)); o = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)   # STL stores each triangle's corners separately
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    pieces, seen = 0, set()
    for f in bm.faces:
        if f.index in seen:
            continue
        pieces += 1; stack = [f]; seen.add(f.index)
        while stack:
            for e in stack.pop().edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index); stack.append(h)
    thin = 0.0
    if not nm:
        bm.normal_update(); tree = BVHTree.FromBMesh(bm)
        for f in bm.faces:
            hit = tree.ray_cast(f.calc_center_median() - f.normal * 1e-4, -f.normal, MIN_WALL)
            if hit[0] is not None and hit[3] < MIN_WALL - 0.02:
                thin += f.calc_area()
    d = sorted(o.dimensions)
    faults = [k for k, b in (("non-manifold", nm), ("inside out", vol < 0), ("too big for the bed", d[-1] > BED)) if b]
    note = "FIX: " + ", ".join(faults) if faults else "ok"
    bad += bool(faults)
    print(f"{name[-43:]:<44}{len(bm.faces):>8}{nm:>8}{pieces:>7}{thin:>10.0f}  {[round(x, 1) for x in o.dimensions]}  {note}")
    bm.free()
print(f"{bad} file(s) need a fix")
sys.exit(1 if bad else 0)
