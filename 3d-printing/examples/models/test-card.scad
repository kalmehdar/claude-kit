// parts: red blue white black
// Four-colour test card: the first print on a new multi-head (toolchanger or AMS-style) printer.
// A 4 x 4 grid where every colour sits next to every other colour once (a Latin square), with each colour's name
// printed into its block on top. If the colours stay crisp at every boundary, purge and retraction are right.
// One STL per colour; load them as one object in your slicer and give each part its own head.
//   part = "red" | "blue" | "white" | "black"  one colour
//   part = "all"                               preview of the whole card
part = "all";
$fn = 48;
font = "Liberation Sans:style=Bold";
inlay = 0.6;                          // depth of the names, printed in the contrasting colour

NAMES = ["red", "blue", "white", "black"];
HEX   = ["#c8102e", "#002fa7", "#f2f2f2", "#1a1a1a"];
LABEL = ["RED", "BLUE", "WHT", "BLK"];
w = 56; cw = w / 4; ch = 7; t = 2.0; top = 13;   // 56 x 41 mm: 14 x 7 mm cells, name row on top
GRID = [[0, 1, 2, 3], [2, 3, 0, 1], [1, 0, 3, 2], [3, 2, 1, 0]];   // rows bottom to top, colour indices

module region(k) {   // every area of colour k, full thickness
  // 0.01 mm bigger all round: same-colour squares meet only corner to corner, and touching exactly they make a
  // non-manifold edge that slicers complain about. The tiny overlap joins them.
  for (r = [0 : 3], c = [0 : 3]) if (GRID[r][c] == k) translate([c * cw - 0.01, r * ch - 0.01, 0]) cube([cw + 0.02, ch + 0.02, t]);
  translate([k * cw, 4 * ch, 0]) cube([cw, top, t]);
}
module name(k, h) translate([k * cw + cw / 2, 4 * ch + top / 2, t - h + 0.01])
  linear_extrude(h) text(LABEL[k], size = 3.2, font = font, halign = "center", valign = "center");
function ink(k) = k == 2 ? 3 : 2;    // name colour: black on the white block, white on the others
module colour_part(k) {              // everything printed in colour k
  difference() { region(k); for (j = [0 : 3]) name(j, inlay + 0.01); }
  for (j = [0 : 3]) if (ink(j) == k) intersection() { name(j, inlay); region(j); }
}

if (part == "all") for (k = [0 : 3]) color(HEX[k]) colour_part(k);
for (k = [0 : 3]) if (part == NAMES[k]) color(HEX[k]) colour_part(k);
