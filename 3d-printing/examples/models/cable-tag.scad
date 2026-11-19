// parts: power data storage other ids_light ids_dark
// Clip-on cable tags, colour-coded by what the lead carries, with an ID printed into the face.
// Each tag's C-clip is sized to its own lead: one bore for every cable fits none of them well.
// Measure each lead type with calipers and set LEADS (outside diameter plus about 0.2 mm).
// Prints flat, ID face down, two heads per tag (tag colour + ID colour). Print two of each, one per end.
//   part = "power" | "data" | "storage" | "other"   tag bodies of that colour
//   part = "ids_light" | "ids_dark"                 the printed-in IDs (white on dark tags, black on white ones)
//   part = "all"                                    preview
part = "all";
$fn = 48;
font = "Liberation Sans:style=Bold";
inlay = 0.6;
tag_w = 22; tag_h = 11; tag_t = 1.8;

// Lead types and their outside diameters, mm. EXAMPLES: measure yours.
LEADS = [["mains", 7.4], ["cat6", 6.2], ["slim", 3.9], ["usb", 4.2], ["dc", 3.6], ["hdmi", 7.2]];
// Your leads: [ID, kind (sets the colour), lead type (sets the clip)]
TAGS = [["P1", "power", "mains"], ["P2", "power", "mains"], ["P3", "power", "dc"],
        ["D1", "data", "slim"], ["D2", "data", "slim"], ["D3", "data", "cat6"],
        ["S1", "storage", "usb"], ["S2", "storage", "usb"], ["V1", "other", "hdmi"]];
KIND = [["power", "#c8102e"], ["data", "#002fa7"], ["storage", "#f2f2f2"], ["other", "#1a1a1a"]];

function bore(type) = [for (l = LEADS) if (l[0] == type) l[1]][0];
module at(i) translate([(i % 5) * 40, floor(i / 5) * 18, 0]) children();
module shape(d) difference() {
  union() { translate([-1.2, -tag_h / 2, 0]) cube([tag_w + 1.2, tag_h, tag_t]); translate([-d / 2 - 1.6, 0, 0]) cylinder(d = d + 3.2, h = tag_h); }
  translate([-d / 2 - 1.6, 0, -1]) cylinder(d = d, h = tag_h + 2);                      // the bore
  translate([-d - 3.2, -d * 0.35, -1]) cube([d / 2, d * 0.7, tag_h + 2]);               // the opening it snaps through
}
module id_text(s, h) translate([tag_w / 2 + 1, 0, -0.01]) mirror([1, 0, 0]) linear_extrude(h)
  text(s, size = 5, font = font, halign = "center", valign = "center");                 // mirrored: it prints face down
module body(kind) for (i = [0 : len(TAGS) - 1]) if (TAGS[i][1] == kind) at(i) difference() { shape(bore(TAGS[i][2])); id_text(TAGS[i][0], inlay + 0.01); }
module ids(dark) for (i = [0 : len(TAGS) - 1]) if ((TAGS[i][1] == "storage") == dark) at(i)
  intersection() { id_text(TAGS[i][0], inlay + 0.01); translate([0, -tag_h, 0]) cube([tag_w + 4, 2 * tag_h, inlay]); }

for (k = KIND) if (part == k[0] || part == "all") color(k[1]) body(k[0]);
if (part == "ids_light" || part == "all") color("#f2f2f2") ids(false);
if (part == "ids_dark" || part == "all") color("#1a1a1a") ids(true);
