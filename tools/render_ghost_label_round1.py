"""Scratch explorer for the GHOST roll-result banner integration (round 1).

Renders the FULL ghost medallion 5 times — once per integration treatment for the
"GHOST" wordmark — each at the true downscaled popup size, tiled into ONE labelled
review figure on a neutral sky-blue field. Reuses the real warren_celebration build
(wheel/studs/hub/bauble) so the explorations read exactly like the shipped medallion;
only the GHOST-label treatment differs per cell. Does NOT modify game/ code.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_ghost_label_round1.py
"""
import math
import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # noqa: E402
from game.draw import _shade_c  # noqa: E402
from game.pillar_staff import (  # noqa: E402
    PLUM_DK, LIME_DK, GOLD, GOLD_DK,
    _mini_clown_face, _marotte_ruff,
)
from game.warren_celebration import (  # noqa: E402
    DW, DH, WHEEL_A_G, WHEEL_B_G,
    GH_METAL, GH_METAL_HI, GH_INDIGO, GH_INDIGO_DK, GH_CREAM,
    _wheel, _gold_stud, _ghostify,
)

ROLL = 10               # the ghost roll always lands on the range minimum
SKY = (150, 200, 235)


# ─── per-glyph arc text (pygame has no native arc-text) ──────────────────────
def _arc_text(canvas, text, cx, cy, radius, ss, *, size, fill, edge, edge_w,
              span_deg, mid_deg=-90.0, shadow_a=0, letter_spacing=1.0,
              face_out=True):
    """Lay each glyph rotated tangent to a circle of `radius` centred at (cx,cy),
    spread across `span_deg` and centred on `mid_deg` (screen angle, -90 = top).
    A thick outline ring + the fill stamped LAST keeps counters open; favours
    chunky bold letterforms that survive the downscale. `face_out=True` seats
    text on the OUTSIDE of the arc (top banderole); False hangs it under the arc
    (bottom ribbon) so the baseline curves with the rim."""
    f = hud._font(int(size * ss), True)
    glyphs = [g for g in text]
    # Weight each glyph by its rendered width so spacing follows the type, not a
    # flat per-character step — keeps "GHOST" optically even on the curve.
    widths = [max(1, f.render(g, True, fill).get_width()) for g in glyphs]
    total = sum(widths) * letter_spacing
    # Arc length the word should occupy → its angular span at this radius.
    span = math.radians(span_deg)
    mid = math.radians(mid_deg)
    # Increasing screen angle runs clockwise; on the BOTTOM arc (face_out=False)
    # that walks the word right-to-left, so flip the angular sweep there to keep
    # "GHOST" reading left-to-right.
    if not face_out:
        span = -span
    cursor = -span * 0.5
    for g, w in zip(glyphs, widths):
        frac = (w * letter_spacing) / total
        ga = cursor + span * frac * 0.5          # glyph centre angle along the arc
        cursor += span * frac
        ang = mid + ga
        gx = cx + math.cos(ang) * radius
        gy = cy + math.sin(ang) * radius
        # Tangent rotation: top banderole text rolls so its baseline hugs the arc.
        rot = -math.degrees(ang) - 90.0
        if not face_out:
            rot += 180.0

        def _stamp(col, alpha=255):
            s = f.render(g, True, col)
            if alpha < 255:
                s.set_alpha(alpha)
            r = pygame.transform.rotate(s, rot)
            canvas.blit(r, r.get_rect(center=(int(gx), int(gy))))

        if shadow_a:
            _stamp((0, 0, 0), shadow_a)
        o = edge_w * ss
        for da in range(0, 360, 30):
            ox = math.cos(math.radians(da)) * o
            oy = math.sin(math.radians(da)) * o
            s = f.render(g, True, edge)
            r = pygame.transform.rotate(s, rot)
            canvas.blit(r, r.get_rect(center=(int(gx + ox), int(gy + oy))))
        _stamp(fill)


def _flat_text(canvas, text, cx, cy, ss, *, size, fill, edge, edge_w,
               shadow_a=120, condense=1.0):
    """Straight bold wordmark with a drop shadow + thick outline ring, fill last.
    `condense` (<1) squeezes the glyph advance so a long word fits a tight disc
    without going thin — the carnival 'tall condensed' read at small size."""
    f = hud._font(int(size * ss), True)
    glyphs = list(text)
    surfs = [f.render(g, True, fill) for g in glyphs]
    edges = [f.render(g, True, edge) for g in glyphs]
    shads = [f.render(g, True, (0, 0, 0)) for g in glyphs]
    advances = [s.get_width() * condense for s in surfs]
    total = sum(advances)
    h = max(s.get_height() for s in surfs)
    x0 = cx - total / 2
    o = edge_w * ss
    # Shadow pass.
    x = x0
    for sh, adv, base in zip(shads, advances, surfs):
        sh.set_alpha(shadow_a)
        canvas.blit(sh, sh.get_rect(center=(int(x + base.get_width() / 2 + 2 * ss),
                                            int(cy + 3 * ss))))
        x += adv
    # Outline pass.
    for da in range(0, 360, 30):
        ox = math.cos(math.radians(da)) * o
        oy = math.sin(math.radians(da)) * o
        x = x0
        for eg, adv, base in zip(edges, advances, surfs):
            canvas.blit(eg, eg.get_rect(center=(int(x + base.get_width() / 2 + ox),
                                                int(cy + oy))))
            x += adv
    # Fill pass last so counters stay open.
    x = x0
    for s, adv in zip(surfs, advances):
        canvas.blit(s, s.get_rect(center=(int(x + s.get_width() / 2), int(cy))))
        x += adv


# ─── the shared medallion build (mirrors warren_celebration.render) ──────────
def _medallion(option, ss=4, b_hr_ss=24):
    """Build the spectral ghost medallion at supersample `ss`, then route the
    GHOST wordmark through one of the 5 integration treatments. Returns the
    DW*ss x DH*ss SRCALPHA canvas (caller downscales)."""
    hdw, hdh = DW * ss, DH * ss
    cx = hdw // 2
    canvas = pygame.Surface((hdw, hdh), pygame.SRCALPHA)

    R = int(hdw * 0.27)
    wcy = int(hdh * 0.60)
    a_col, b_col = WHEEL_A_G, WHEEL_B_G
    metal, metal_hi = GH_METAL, GH_METAL_HI
    ring, disc, spoke = GH_INDIGO, GH_CREAM, GH_INDIGO_DK

    _wheel(canvas, cx, R, ss, 8, a_col, b_col, spin=0.42, rim=metal, rim_w=7,
           cy=wcy, hi=metal_hi, spoke=spoke)
    for i in range(1, 4):
        a = i * math.tau / 4 - math.pi / 2
        sx = cx + math.cos(a) * (R + int(2 * ss))
        sy = wcy + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss, col=metal, hi=metal_hi)

    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, ring, (cx, wcy), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, metal, (cx, wcy), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, disc, (cx, wcy), hub_r)
    pygame.draw.circle(canvas, ring, (cx, wcy), hub_r, max(2, int(2 * ss)))

    b_hr = int(b_hr_ss * ss)
    b_hy = (wcy - R) - int(0.95 * b_hr)

    # Bauble first (it crowns the top); for options that arc text over the rim we
    # draw the arc AFTER so the wordmark frames around the bauble, not behind it.
    def _draw_bauble():
        blayer = pygame.Surface((hdw, hdh), pygame.SRCALPHA)
        _jester_bauble(blayer, cx, b_hy, b_hr, ss)
        _ghostify(blayer)
        canvas.blit(blayer, (0, 0))

    # ── Option 1: GHOST OWNS THE HUB ─────────────────────────────────────────
    # The word replaces the number entirely — fitted/condensed across the cream
    # disc as the hero, two lines so the chunky letters stay big inside the round.
    if option == 1:
        _draw_bauble()
        # Two stacked rows fill the round disc better than one squeezed line.
        _flat_text(canvas, "GHO", cx, wcy - int(hub_r * 0.34), ss,
                   size=42, fill=ring, edge=disc, edge_w=4, shadow_a=90,
                   condense=0.92)
        _flat_text(canvas, "ST", cx, wcy + int(hub_r * 0.36), ss,
                   size=42, fill=ring, edge=disc, edge_w=4, shadow_a=90,
                   condense=0.92)

    # ── Option 2: ARCHED BANDEROLE OVER THE TOP RIM ──────────────────────────
    # "GHOST" curved along the upper arc of the rim, wrapping AROUND the bauble
    # like a carnival header. The number stays the hero in the hub.
    elif option == 2:
        _draw_bauble()
        _num_block(canvas, cx, wcy, ROLL, ss, ring, disc)
        # A faint icy keyline arc under the text reads as a header band.
        band_r = R + int(15 * ss)
        pygame.draw.arc(canvas, GH_INDIGO_DK,
                        (cx - band_r, wcy - band_r, band_r * 2, band_r * 2),
                        math.radians(205), math.radians(335), max(2, int(3 * ss)))
        _arc_text(canvas, "GHOST", cx, wcy, band_r, ss,
                  size=30, fill=GH_CREAM, edge=GH_INDIGO_DK, edge_w=4,
                  span_deg=118, mid_deg=-90, shadow_a=110, face_out=True)

    # ── Option 3: LOWER-ARC RIBBON WOVEN INTO THE RIM ────────────────────────
    # A periwinkle ribbon wraps the bottom of the wheel, anchored under the
    # bottom stud, its swallow-tail ends curling past the rim — text follows the
    # lower curve. Integrated to the rim, not floating free.
    elif option == 3:
        _draw_bauble()
        _num_block(canvas, cx, wcy, ROLL, ss, ring, disc)
        _bottom_ribbon(canvas, cx, wcy, R, ss)
        rib_r = R + int(14 * ss)
        _arc_text(canvas, "GHOST", cx, wcy, rib_r, ss,
                  size=27, fill=GH_CREAM, edge=GH_INDIGO_DK, edge_w=3,
                  span_deg=104, mid_deg=90, shadow_a=110, face_out=False)

    # ── Option 4: GHOST STACKED WITH THE NUMBER IN THE HUB ───────────────────
    # A small arched "GHOST" rides the top inner edge of the cream disc, the big
    # number seated just below it — both own the hub, no detached plate.
    elif option == 4:
        _draw_bauble()
        # Arched word along the inner top of the disc.
        _arc_text(canvas, "GHOST", cx, wcy + int(hub_r * 0.18),
                  int(hub_r * 0.80), ss,
                  size=18, fill=ring, edge=disc, edge_w=3,
                  span_deg=112, mid_deg=-90, shadow_a=70, face_out=True)
        # Number dropped a touch + shrunk so the stacked word has room.
        _num_block(canvas, cx, wcy + int(hub_r * 0.20), ROLL, ss, ring, disc,
                   size=58)

    # ── Option 5: SPECTRAL NAMEPLATE INSET INTO THE WHEEL FACE ───────────────
    # A long icy-chrome nameplate bar inset across the wheel face, riveted into
    # the rim at both ends, GHOST stamped on it — part of the wheel hardware, not
    # a plate beneath it. The number stays the hero in the hub above it.
    elif option == 5:
        _draw_bauble()
        _num_block(canvas, cx, wcy - int(R * 0.06), ROLL, ss, ring, disc, size=72)
        _inset_nameplate(canvas, cx, wcy + int(R * 0.70), R, ss)

    return canvas


def _jester_bauble(canvas, cx, hy, hr, ss):
    """Local copy of warren_celebration._jester_bauble (module-private), so the
    explorations crown with the real mini-clown bauble without importing a name
    the module doesn't export."""
    u = hr / (13.0 * ss)
    base_y = hy - hr + int(1 * ss)
    span = max(2, int(8 * ss * u))
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp = cx + int(dx * ss * u)
        byp = base_y + int(dy * ss * u)
        tri = [(cx - span, base_y + int(2 * ss)),
               (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(canvas, col, tri)
        pygame.draw.polygon(canvas, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)),
                             (cx, base_y + int(2 * ss)), (bxp, byp)])
        pygame.draw.polygon(canvas, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        br = max(2, int(3.4 * ss * u))
        pygame.draw.circle(canvas, GOLD, (int(bxp), int(byp)), br)
        pygame.draw.circle(canvas, GOLD_DK, (int(bxp), int(byp)), br, max(1, int(ss)))
    _marotte_ruff(canvas, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, (132, 218, 116), lobes=9)
    _mini_clown_face(canvas, cx, hy, hr, ss, expr="grin")


def _num_block(canvas, c, ncy, roll, ss, num_col, edge_col, *, size=88,
               shadow_a=110, edge_w=4):
    """Local copy of warren_celebration._num_block (module-private)."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    for ang in range(0, 360, 15):
        ox = math.cos(math.radians(ang)) * o
        oy = math.sin(math.radians(ang)) * o
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    canvas.blit(num, num.get_rect(center=(c, ncy)))


def _bottom_ribbon(canvas, cx, wcy, R, ss):
    """A periwinkle banner ribbon wrapping the LOWER rim — a curved centre band
    that follows the wheel edge with two swallow-tail ends flaring past the rim,
    plus an icy keyline. Anchored to the rim so it reads woven in, not floating."""
    plate, hi, dk = GH_INDIGO, GH_METAL, GH_INDIGO_DK
    # Centre band: an annulus slice hugging the lower rim, built from a polygon
    # ring between two radii across the bottom arc.
    r_out = R + int(22 * ss)
    r_in = R + int(2 * ss)
    a0, a1 = math.radians(40), math.radians(140)
    outer, inner = [], []
    n = 28
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        outer.append((cx + math.cos(a) * r_out, wcy + math.sin(a) * r_out))
        inner.append((cx + math.cos(a) * r_in, wcy + math.sin(a) * r_in))
    band = outer + list(reversed(inner))
    # Swallow-tail ends: a notched flag tail at each side of the band.
    for s, a in ((-1, a1), (1, a0)):
        ax = cx + math.cos(a) * ((r_out + r_in) / 2)
        ay = wcy + math.sin(a) * ((r_out + r_in) / 2)
        outx = cx + math.cos(a) * (r_out + int(18 * ss))
        outy = wcy + math.sin(a) * (r_out + int(18 * ss))
        tang = a + s * math.pi / 2
        tx, ty = math.cos(tang), math.sin(tang)
        tail = [
            (cx + math.cos(a) * r_out, wcy + math.sin(a) * r_out),
            (outx + tx * 14 * ss, outy + ty * 14 * ss),
            (outx - tx * 4 * ss + math.cos(a) * 3 * ss,
             outy - ty * 4 * ss + math.sin(a) * 3 * ss),  # notch
            (cx + math.cos(a) * r_in, wcy + math.sin(a) * r_in),
        ]
        pygame.draw.polygon(canvas, dk, [(int(p[0]), int(p[1])) for p in tail])
        pygame.draw.polygon(canvas, plate,
                            [(int(p[0]), int(p[1])) for p in tail][:-1] +
                            [(int(tail[-1][0]), int(tail[-1][1]))])
    pygame.draw.polygon(canvas, dk, [(int(p[0]), int(p[1])) for p in band])
    pygame.draw.polygon(canvas, plate,
                        [(int(p[0]), int(p[1])) for p in
                         (outer[1:-1] + list(reversed(inner[1:-1])))])
    # Icy keyline along the ribbon's outer + inner edge.
    pygame.draw.lines(canvas, hi, False, [(int(p[0]), int(p[1])) for p in outer],
                      max(1, int(2 * ss)))
    pygame.draw.lines(canvas, _shade_c(plate, -40), False,
                      [(int(p[0]), int(p[1])) for p in inner], max(1, int(ss)))


def _inset_nameplate(canvas, cx, cy, R, ss):
    """An icy-chrome nameplate bar inset across the wheel face, ground into the
    rim at both ends with two studs — reads as wheel hardware. GHOST stamped on
    the cool-cream face of the bar."""
    metal, metal_hi, metal_dk = GH_METAL, GH_METAL_HI, (84, 138, 176)
    w = int(R * 1.66)
    h = int(34 * ss)
    rect = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    rr = int(10 * ss)
    # Chrome frame + cool-cream inset face.
    pygame.draw.rect(canvas, metal_dk, rect.inflate(int(6 * ss), int(6 * ss)),
                     border_radius=rr + int(2 * ss))
    pygame.draw.rect(canvas, metal, rect.inflate(int(2 * ss), int(2 * ss)),
                     border_radius=rr)
    pygame.draw.rect(canvas, GH_INDIGO, rect, border_radius=rr)
    pygame.draw.rect(canvas, metal_hi, rect, max(1, int(2 * ss)), border_radius=rr)
    # End studs ground into the rim.
    for s in (-1, 1):
        sx = cx + s * (w / 2 + int(4 * ss))
        _gold_stud(canvas, sx, cy, int(8 * ss), ss, col=metal, hi=metal_hi)
    _flat_text(canvas, "GHOST", cx, cy, ss, size=22, fill=GH_CREAM,
               edge=GH_INDIGO_DK, edge_w=3, shadow_a=110, condense=0.96)


# ─── assemble the labelled review sheet ──────────────────────────────────────
def main():
    os.makedirs("/home/user/skybit/docs/ghost_label", exist_ok=True)

    titles = {
        1: "1  GHOST owns the hub",
        2: "2  Arched banderole over rim",
        3: "3  Lower-arc woven ribbon",
        4: "4  GHOST + number stacked in hub",
        5: "5  Inset spectral nameplate",
    }

    # Render each option at the true downscaled popup size (264x360), then crop to
    # the medallion's vertical extent so the on-screen read (~170 px tall) is shown.
    tiles = []
    for opt in range(1, 6):
        big = _medallion(opt, ss=4)
        full = pygame.transform.smoothscale(big, (DW, DH))
        tiles.append((opt, full))

    # Grid: 2 columns x 3 rows (5 cells + a caption header), each cell on the
    # neutral sky field with a title strip, drawn at real on-screen scale.
    cell_w, cell_h = DW + 30, DH + 56
    cols, rows = 3, 2
    margin = 24
    header_h = 64
    sheet_w = cols * cell_w + (cols + 1) * margin
    sheet_h = header_h + rows * cell_h + (rows + 1) * margin
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SKY)

    title_f = hud._font(34, True)
    sub_f = hud._font(18, True)
    head = title_f.render("Skybit  -  GHOST banner integration  -  round 1",
                          True, (28, 30, 70))
    sheet.blit(head, head.get_rect(midleft=(margin, header_h // 2 + 8)))
    note = sub_f.render("full ghost medallion, real on-screen popup size",
                        True, (40, 56, 110))
    sheet.blit(note, note.get_rect(midleft=(margin, header_h // 2 + 38)))

    cap_f = hud._font(20, True)
    for idx, (opt, tile) in enumerate(tiles):
        col = idx % cols
        row = idx // cols
        cx0 = margin + col * (cell_w + margin)
        cy0 = header_h + margin + row * (cell_h + margin)
        cell = pygame.Rect(cx0, cy0, cell_w, cell_h)
        pygame.draw.rect(sheet, (132, 184, 222), cell, border_radius=14)
        pygame.draw.rect(sheet, (90, 140, 190), cell, 2, border_radius=14)
        # Medallion centred in the cell, leaving room for the caption strip.
        sheet.blit(tile, tile.get_rect(center=(cell.centerx, cy0 + 16 + DH // 2)))
        cap = cap_f.render(titles[opt], True, (24, 26, 64))
        sheet.blit(cap, cap.get_rect(midbottom=(cell.centerx, cell.bottom - 12)))

    out = "/home/user/skybit/docs/ghost_label/round_1.png"
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
