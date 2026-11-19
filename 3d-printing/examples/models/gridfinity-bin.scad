// parts: cset_body cset_band_red cset_band_blue cset_band_white cset_text_light cset_text_dark
// Gridfinity bins with the label printed into the front (no stickers). Standard 42 mm grid, 7 mm height units
// and the standard foot, so they drop into any Gridfinity baseplate. Gridfinity is Zack Freedman's open standard.
//   part = "body" (black) or "label" (white); gx, gy cells; hu height units (7 mm each); label text
//   part = "set" / "set_labels": all eight bins laid out on the tray, for the rack view
part = "body";
gx = 1; gy = 1; hu = 6; label = "SCREWS";   // 6 units = 42 mm tall
pitch = 42; gap = 0.5; wall = 1.2; floor_t = 1.2; r_out = 3.75;
foot_h = 4.75;                  // 0.8 + 1.8 + 2.15, the inverse of the baseplate's pocket
inlay = 0.6;
font = "Liberation Sans:style=Bold";
$fn = 32;

module rsq(w, d, r, z, t = 0.01) translate([0, 0, z]) linear_extrude(t) offset(r = r) square([w - 2 * r, d - 2 * r], center = true);
module foot() {   // one cell's foot, top at foot_h
  w = pitch - gap;
  hull() { rsq(w - 2 * 2.95, w - 2 * 2.95, 0.8, 0); rsq(w - 2 * 2.15, w - 2 * 2.15, 1.6, 0.8); }
  hull() { rsq(w - 2 * 2.15, w - 2 * 2.15, 1.6, 0.8); rsq(w - 2 * 2.15, w - 2 * 2.15, 1.6, 2.6); }
  hull() { rsq(w - 2 * 2.15, w - 2 * 2.15, 1.6, 2.6); rsq(w, w, r_out, foot_h); }
}
// The tray set (5 x 5 cells). [gx, gy, x cell, y cell, label]
SET = [[2, 1, 0, 0, "KEYSTONES"], [1, 1, 2, 0, "SCREWS"], [2, 1, 3, 0, "VELCRO"],
       [2, 2, 0, 1, "ADAPTERS"], [1, 1, 2, 1, "NFC"], [2, 1, 3, 1, "LEAD TAGS"],
       [1, 1, 2, 2, "USB"], [2, 2, 3, 2, "SPARE LEADS"],
       [2, 2, 0, 3, "SPARES"], [1, 2, 2, 3, "MISC"], [2, 1, 3, 4, "TOOLS"]];   // all 25 cells
module at(b) translate([(b[2] + b[0] / 2 - 2.5) * pitch, (b[3] + b[1] / 2 - 2.5) * pitch, 0]) children();
if (part == "body") color("#1a1a1a") bin_n(gx, gy, label, false);
if (part == "label") color("#f2f2f2") bin_n(gx, gy, label, true);
if (part == "set") for (b = SET) at(b) color("#1a1a1a") bin_n(b[0], b[1], b[4], false);
if (part == "set_labels") for (b = SET) at(b) color("#f2f2f2") bin_n(b[0], b[1], b[4], true);

// ---- colour-coded set (four heads) ----
// A band across the front in the bin's colour (the same code as cable-tag.scad), the name printed into it.
// Red power, blue network, white storage; other bins keep white text on black. Parts, one per head:
//   cset_body (black), cset_band_red, cset_band_blue, cset_band_white, cset_text_light (white), cset_text_dark (black)
function cat(t) = t == "ADAPTERS" || t == "USB" ? "red"
                : t == "KEYSTONES" || t == "SPARE LEADS" || t == "LEAD TAGS" ? "blue"
                : t == "NFC" ? "white" : "none";
CHEX = [["red", "#c8102e"], ["blue", "#002fa7"], ["white", "#f2f2f2"]];
band_h = 9;
// The whole set plus a four-colour prime tower does not fit a 270 mm bed in one go, so it
// prints as two plates: cs0..cs1 picks the bins (0-5 the first six, 6-10 the rest), each at its place in the tray.
cs0 = 0; cs1 = len(SET) - 1;
module band(nx, ny) let(w = nx * pitch - gap, d = ny * pitch - gap, h = hu * 7)   // the band's area on the front face
  translate([0, -d / 2 - 0.01, foot_h + (h - foot_h) * 0.55]) rotate([90, 0, 0]) mirror([0, 0, 1])
    linear_extrude(inlay + 0.01) offset(r = 1.5) square([w - 11, band_h - 3], center = true);
module ctext(nx, ny, txt) let(w = nx * pitch - gap, d = ny * pitch - gap, h = hu * 7)
  translate([0, -d / 2 - 0.01, foot_h + (h - foot_h) * 0.55]) rotate([90, 0, 0]) mirror([0, 0, 1])
    linear_extrude(inlay + 0.01) text(txt, size = min(5, (w - 8) / max(1, len(txt)) * 1.45), font = font, halign = "center", valign = "center");
module cbin_body(b) if (cat(b[4]) == "none") bin_n(b[0], b[1], b[4], false);
  else difference() { bin_n(b[0], b[1], "", false); band(b[0], b[1]); }
if (part == "cset_body") for (k = [cs0 : cs1]) let(b = SET[k]) at(b) color("#1a1a1a") cbin_body(b);
for (c = CHEX) if (part == str("cset_band_", c[0]))
  for (k = [cs0 : cs1]) let(b = SET[k]) if (cat(b[4]) == c[0]) at(b) color(c[1]) difference() { band(b[0], b[1]); ctext(b[0], b[1], b[4]); }
if (part == "cset_text_light") for (k = [cs0 : cs1]) let(b = SET[k]) if (cat(b[4]) != "white") at(b) color("#f2f2f2")
  intersection() { ctext(b[0], b[1], b[4]); if (cat(b[4]) == "none") bin_n(b[0], b[1], b[4], true); else band(b[0], b[1]); }
if (part == "cset_text_dark") for (k = [cs0 : cs1]) let(b = SET[k]) if (cat(b[4]) == "white") at(b) color("#1a1a1a") intersection() { ctext(b[0], b[1], b[4]); band(b[0], b[1]); }
if (part == "cset_all") { for (k = [cs0 : cs1]) let(b = SET[k]) at(b) color("#1a1a1a") cbin_body(b);
  for (c = CHEX) for (k = [cs0 : cs1]) let(b = SET[k]) if (cat(b[4]) == c[0]) at(b) color(c[1]) difference() { band(b[0], b[1]); ctext(b[0], b[1], b[4]); }
  for (k = [cs0 : cs1]) let(b = SET[k]) at(b) color(cat(b[4]) == "white" ? "#1a1a1a" : "#f2f2f2") intersection() { ctext(b[0], b[1], b[4]); if (cat(b[4]) == "none") bin_n(b[0], b[1], b[4], true); else band(b[0], b[1]); } }
module bin_n(nx, ny, txt, lab) {
  w = nx * pitch - gap; d = ny * pitch - gap; h = hu * 7;
  module lt(hh) translate([0, -d / 2 - 0.01, foot_h + (h - foot_h) * 0.55]) rotate([90, 0, 0]) mirror([0, 0, 1])
    linear_extrude(hh) text(txt, size = min(5, (w - 8) / max(1, len(txt)) * 1.45), font = font, halign = "center", valign = "center");
  if (lab) intersection() { lt(inlay + 0.01); translate([-w / 2, -d / 2, 0]) cube([w, inlay, h]); }
  else difference() {
    union() {
      for (i = [0 : nx - 1], j = [0 : ny - 1]) translate([(i - (nx - 1) / 2) * pitch, (j - (ny - 1) / 2) * pitch, 0]) foot();
      hull() { rsq(w, d, r_out, foot_h); rsq(w, d, r_out, h - 0.01); }
    }
    hull() { rsq(w - 2 * wall, d - 2 * wall, r_out - wall, foot_h + floor_t); rsq(w - 2 * wall, d - 2 * wall, r_out - wall, h + 1); }
    lt(inlay + 0.01);
  }
}
