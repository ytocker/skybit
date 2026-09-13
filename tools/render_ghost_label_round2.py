"""Scratch explorer for the GHOST roll-result banner integration (round 2).

Round-1 chose V5 (inset spectral nameplate) as the lead, V3 (swallow-tail ribbon)
as the alternative. This sheet refines V5 into three sub-variants (A straight, B
riveted end-caps, C downward-curved banner) plus one refined V3, four cells on the
real sky-blue popup field. Reuses the shipped warren_celebration medallion build so
the explorations read exactly like the live medallion; only the GHOST treatment
differs. Does NOT modify game/ code.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_ghost_label_round2.py
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
    GH_METAL, GH_METAL_HI, GH_METAL_DK, GH_INDIGO, GH_INDIGO_DK, GH_CREAM,
    _wheel, _gold_stud, _ghostify,
)

ROLL = 10               # the ghost roll always lands on the range minimum
SKY = (150, 200, 235)


# ─── flat bold wordmark (single solid fill, one keyline, drop shadow) ─────────
def _flat_text(canvas, text, cx, cy, ss, *, size, fill, edge, edge_w,
               shadow_a=120, condense=1.0, letter_spacing=1.0):
    """Straight bold wordmark: drop shadow, ONE thick outline ring, fill stamped
    last so counters stay open. `letter_spacing`>1 opens the tracking; `condense`
    squeezes the glyph advance. Single solid fill — no per-letter bubble outline,
    which smears at the ~170px downscale."""
    f = hud._font(int(size * ss), True)
    glyphs = list(text)
    surfs = [f.render(g, True, fill) for g in glyphs]
    edges = [f.render(g, True, edge) for g in glyphs]
    shads = [f.render(g, True, (0, 0, 0)) for g in glyphs]
    advances = [s.get_width() * condense * letter_spacing for s in surfs]
    total = sum(advances)
    x0 = cx - total / 2
    o = edge_w * ss
    x = x0
    for sh, adv, base in zip(shads, advances, surfs):
        sh.set_alpha(shadow_a)
        canvas.blit(sh, sh.get_rect(center=(int(x + adv / 2 + 2 * ss),
                                            int(cy + 3 * ss))))
        x += adv
    for da in range(0, 360, 30):
        ox = math.cos(math.radians(da)) * o
        oy = math.sin(math.radians(da)) * o
        x = x0
        for eg, adv in zip(edges, advances):
            canvas.blit(eg, eg.get_rect(center=(int(x + adv / 2 + ox),
                                                int(cy + oy))))
            x += adv
    x = x0
    for s, adv in zip(surfs, advances):
        canvas.blit(s, s.get_rect(center=(int(x + adv / 2), int(cy))))
        x += adv


def _arc_text(canvas, text, cx, cy, radius, ss, *, size, fill, edge, edge_w,
              span_deg, mid_deg=-90.0, shadow_a=0, letter_spacing=1.0,
              face_out=True):
    """Per-glyph arc text rotated tangent to a circle, fill stamped last over a
    single outline ring — for the curved nameplate (C) and the swallow-tail (V3)."""
    f = hud._font(int(size * ss), True)
    glyphs = [g for g in text]
    widths = [max(1, f.render(g, True, fill).get_width()) for g in glyphs]
    total = sum(widths) * letter_spacing
    span = math.radians(span_deg)
    mid = math.radians(mid_deg)
    if not face_out:
        span = -span
    cursor = -span * 0.5
    for g, w in zip(glyphs, widths):
        frac = (w * letter_spacing) / total
        ga = cursor + span * frac * 0.5
        cursor += span * frac
        ang = mid + ga
        gx = cx + math.cos(ang) * radius
        gy = cy + math.sin(ang) * radius
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


# ─── icy-chrome plate fill helpers ───────────────────────────────────────────
def _chrome_vgrad(canvas, rect, rr, ss):
    """Fill a rounded-rect with a top-down light->mid periwinkle vertical gradient
    so the plate reads as the same brushed icy metal as the rim. Built on a clipped
    SRCALPHA strip then masked to the rounded rect."""
    top = GH_METAL_HI            # lit top
    bot = _shade_c(GH_METAL, -22)  # mid periwinkle floor
    grad = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = (int(top[0] + (bot[0] - top[0]) * t),
               int(top[1] + (bot[1] - top[1]) * t),
               int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(grad, col, (0, y), (rect.w, y))
    # Mask to the rounded-rect so the gradient only paints inside the plate.
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=rr)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(grad, rect.topleft)


def _plate_shadow(canvas, rect, rr, ss):
    """Soft 1-2px drop shadow under the plate so it sits ON the wheel face."""
    sh = pygame.Surface((rect.w + int(8 * ss), rect.h + int(8 * ss)),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(),
                     border_radius=rr + int(2 * ss))
    canvas.blit(sh, (rect.x - int(4 * ss), rect.y + int(2 * ss)))


# ─── the shared medallion build (mirrors warren_celebration.render) ──────────
def _base_medallion(ss):
    """Build the spectral ghost wheel + studs + hub (no GHOST label, no number) at
    supersample `ss`. Returns (canvas, cx, R, wcy, hub_r) so each variant lays its
    nameplate + number onto an identical medallion."""
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

    b_hr = int(24 * ss)
    b_hy = (wcy - R) - int(0.95 * b_hr)
    blayer = pygame.Surface((hdw, hdh), pygame.SRCALPHA)
    _jester_bauble(blayer, cx, b_hy, b_hr, ss)
    _ghostify(blayer)
    canvas.blit(blayer, (0, 0))

    return canvas, cx, R, wcy, hub_r


def _num_block(canvas, c, ncy, roll, ss, num_col, edge_col, *, size=88,
               shadow_a=110, edge_w=4):
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


def _jester_bauble(canvas, cx, hy, hr, ss):
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
    _marotte_ruff(canvas, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss,
                  (132, 218, 116), lobes=9)
    _mini_clown_face(canvas, cx, hy, hr, ss, expr="grin")


# ─── V5 nameplate refinements (icy chrome, inset into the lower wheel face) ──
def _nameplate_straight(canvas, cx, cy, R, ss, *, rivets=False):
    """Icy-chrome straight nameplate inset into the lower wheel face. A top-down
    light->mid periwinkle vertical gradient fill (same metal as the rim), a 1px top
    highlight keyline, a thin dark keyline around the whole plate, and a soft drop
    shadow so it sits ON the wheel. `rivets` adds a chrome end-cap stud at each end
    (sub-variant B). GHOST opens ~8% tracking, caps ~half the number height, in deep
    navy so it holds contrast on the lighter chrome."""
    w = int(R * (1.58 if rivets else 1.52))
    h = int(30 * ss)
    rect = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    rr = int(9 * ss)

    _plate_shadow(canvas, rect, rr, ss)
    # Thin dark keyline around the whole plate (drawn slightly larger, behind fill).
    pygame.draw.rect(canvas, GH_INDIGO_DK, rect.inflate(int(2 * ss), int(2 * ss)),
                     border_radius=rr + int(1 * ss))
    _chrome_vgrad(canvas, rect, rr, ss)
    # 1px top highlight keyline reads the lit top edge of the brushed metal.
    pygame.draw.line(canvas, GH_METAL_HI,
                     (rect.x + rr, rect.y + max(1, int(ss))),
                     (rect.right - rr, rect.y + max(1, int(ss))), max(1, int(ss)))
    # Crisp metal frame ring tying it to the rim.
    pygame.draw.rect(canvas, GH_METAL_DK, rect, max(1, int(ss)), border_radius=rr)

    if rivets:
        for s in (-1, 1):
            sx = cx + s * (w / 2 - int(3 * ss))
            _gold_stud(canvas, sx, cy, int(7 * ss), ss,
                       col=GH_METAL, hi=GH_METAL_HI)

    _flat_text(canvas, "GHOST", cx, cy - int(1 * ss), ss, size=18,
               fill=GH_INDIGO_DK, edge=GH_CREAM, edge_w=2, shadow_a=70,
               letter_spacing=1.08)


def _nameplate_curved(canvas, cx, wcy, R, ss, hub_r):
    """Sub-variant C: the nameplate as a gently downward-curved chrome banner hugging
    the lower rim arc, inset into the wheel FACE (the annulus between hub and rim) so
    it never slices the hub or the number. Built as an annulus slice band between two
    radii across the bottom arc, top-down chrome-shaded (lit outer -> mid periwinkle
    inner), 1px dark keyline + drop shadow, GHOST per-glyph rotated tangent in deep
    navy so it holds contrast against the light chrome."""
    half_w = int(13 * ss)            # band half-thickness
    # Seat the band so its OUTER edge clears the rim (stays inside R) and its INNER
    # edge clears the hub disc — purely on the lower face, lifted above the stud.
    r_out = R - int(5 * ss)
    r_mid = r_out - half_w
    r_in = r_mid - half_w
    a0, a1 = math.radians(56), math.radians(124)
    n = 30
    outer, inner, mid = [], [], []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        outer.append((cx + math.cos(a) * r_out, wcy + math.sin(a) * r_out))
        inner.append((cx + math.cos(a) * r_in, wcy + math.sin(a) * r_in))
        mid.append((cx + math.cos(a) * r_mid, wcy + math.sin(a) * r_mid))
    band = outer + list(reversed(inner))
    poly = [(int(p[0]), int(p[1])) for p in band]

    # Soft drop shadow nudged down so the curved banner sits on the face.
    sh = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 95),
                        [(int(p[0]), int(p[1] + 2.5 * ss)) for p in band])
    canvas.blit(sh, (0, 0))

    # 1px dark keyline base, then a top-down chrome read: lit upper half in GH_METAL,
    # mid periwinkle lower half — same icy metal as the rim, not a white sticker.
    pygame.draw.polygon(canvas, GH_INDIGO_DK, poly)
    lit = outer + list(reversed(mid))
    shade = mid + list(reversed(inner))
    pygame.draw.polygon(canvas, GH_METAL, [(int(p[0]), int(p[1])) for p in lit])
    pygame.draw.polygon(canvas, GH_METAL_DK,
                        [(int(p[0]), int(p[1])) for p in shade])
    # Top catch-light + bottom dark keyline so the band reads domed.
    pygame.draw.lines(canvas, GH_METAL_HI, False,
                      [(int(p[0]), int(p[1])) for p in outer], max(1, int(ss)))
    pygame.draw.lines(canvas, GH_INDIGO_DK, False,
                      [(int(p[0]), int(p[1])) for p in inner], max(1, int(ss)))

    _arc_text(canvas, "GHOST", cx, wcy, r_mid, ss, size=16,
              fill=GH_INDIGO_DK, edge=GH_METAL_HI, edge_w=2, span_deg=60,
              mid_deg=90, shadow_a=70, letter_spacing=1.08, face_out=False)


# ─── V3 swallow-tail ribbon refinement ───────────────────────────────────────
def _swallow_ribbon(canvas, cx, wcy, R, ss):
    """A periwinkle swallow-tail banner whose CENTRE notch overlaps the bottom rim/
    stud (no floating gap), swallow-tail ends flaring past the rim. Single solid
    GH_CREAM word, ONE GH_INDIGO_DK keyline + soft shadow — no per-letter bubble
    outline. Number stays hero in the hub."""
    plate, hi, dk = GH_INDIGO, GH_METAL, GH_INDIGO_DK
    # Anchor the band high enough that its top edge overlaps the bottom rim + stud.
    r_out = R + int(30 * ss)
    r_in = R - int(4 * ss)           # top edge sits INSIDE the rim -> overlaps stud
    a0, a1 = math.radians(44), math.radians(136)
    n = 28
    outer, inner = [], []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        outer.append((cx + math.cos(a) * r_out, wcy + math.sin(a) * r_out))
        inner.append((cx + math.cos(a) * r_in, wcy + math.sin(a) * r_in))
    band = outer + list(reversed(inner))

    # Soft drop shadow.
    sh = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 110),
                        [(int(p[0]), int(p[1] + 3 * ss)) for p in band])
    canvas.blit(sh, (0, 0))

    # Swallow-tail ends with a V notch.
    for s, a in ((-1, a1), (1, a0)):
        outx = cx + math.cos(a) * (r_out + int(20 * ss))
        outy = wcy + math.sin(a) * (r_out + int(20 * ss))
        tang = a + s * math.pi / 2
        tx, ty = math.cos(tang), math.sin(tang)
        tail = [
            (cx + math.cos(a) * r_out, wcy + math.sin(a) * r_out),
            (outx + tx * 16 * ss, outy + ty * 16 * ss),
            (outx - tx * 5 * ss + math.cos(a) * 4 * ss,
             outy - ty * 5 * ss + math.sin(a) * 4 * ss),
            (cx + math.cos(a) * r_in, wcy + math.sin(a) * r_in),
        ]
        pygame.draw.polygon(canvas, dk,
                            [(int(p[0]), int(p[1])) for p in tail])
        pygame.draw.polygon(canvas, plate,
                            [(int(p[0]), int(p[1])) for p in tail])

    # Centre band: dark keyline base then periwinkle face.
    pygame.draw.polygon(canvas, dk, [(int(p[0]), int(p[1])) for p in band])
    pygame.draw.polygon(canvas, plate,
                        [(int(p[0]), int(p[1])) for p in
                         (outer[1:-1] + list(reversed(inner[1:-1])))])
    pygame.draw.lines(canvas, hi, False,
                      [(int(p[0]), int(p[1])) for p in outer], max(1, int(2 * ss)))
    pygame.draw.lines(canvas, dk, False,
                      [(int(p[0]), int(p[1])) for p in inner], max(1, int(ss)))

    rib_r = R + int(13 * ss)
    _arc_text(canvas, "GHOST", cx, wcy, rib_r, ss, size=24,
              fill=GH_CREAM, edge=GH_INDIGO_DK, edge_w=3, span_deg=92,
              mid_deg=90, shadow_a=110, letter_spacing=1.04, face_out=False)


# ─── per-cell composition ─────────────────────────────────────────────────────
def _cell(variant, ss=4):
    canvas, cx, R, wcy, hub_r = _base_medallion(ss)
    ring, disc = GH_INDIGO, GH_CREAM

    if variant in ("A", "B", "C"):
        # Number pulled up so its baseline clears the inset plate top.
        _num_block(canvas, cx, wcy - int(R * 0.10), ROLL, ss, ring, disc, size=72)
        # Raise the plate ~5px (in true px) into the lower wheel face; it must not
        # clip the bottom cardinal stud (which sits at R + 2*ss below the hub).
        plate_cy = wcy + int(R * 0.62)
        if variant == "A":
            _nameplate_straight(canvas, cx, plate_cy, R, ss, rivets=False)
        elif variant == "B":
            _nameplate_straight(canvas, cx, plate_cy, R, ss, rivets=True)
        else:
            _nameplate_curved(canvas, cx, wcy, R, ss, hub_r)
    else:  # "V3"
        _num_block(canvas, cx, wcy, ROLL, ss, ring, disc, size=88)
        _swallow_ribbon(canvas, cx, wcy, R, ss)

    return pygame.transform.smoothscale(canvas, (DW, DH))


def main():
    os.makedirs("/home/user/skybit/docs/ghost_label", exist_ok=True)

    cells = [
        ("A", "V5-A  straight chrome nameplate"),
        ("B", "V5-B  riveted end-caps"),
        ("C", "V5-C  curved chrome banner"),
        ("V3", "V3  swallow-tail ribbon (alt)"),
    ]
    tiles = [(cap, _cell(v)) for v, cap in cells]

    cell_w, cell_h = DW + 30, DH + 50
    cols, rows = 2, 2
    margin = 24
    header_h = 64
    sheet_w = cols * cell_w + (cols + 1) * margin
    sheet_h = header_h + rows * cell_h + (rows + 1) * margin
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SKY)

    title_f = hud._font(34, True)
    sub_f = hud._font(18, True)
    head = title_f.render("Skybit  -  GHOST banner  -  round 2",
                          True, (28, 30, 70))
    sheet.blit(head, head.get_rect(midleft=(margin, header_h // 2 + 8)))
    note = sub_f.render("V5 nameplate (A/B/C) + V3 alt - icy chrome, number hero, "
                        "true popup size", True, (40, 56, 110))
    sheet.blit(note, note.get_rect(midleft=(margin, header_h // 2 + 38)))

    cap_f = hud._font(20, True)
    for idx, (cap, tile) in enumerate(tiles):
        col = idx % cols
        row = idx // cols
        cx0 = margin + col * (cell_w + margin)
        cy0 = header_h + margin + row * (cell_h + margin)
        cell = pygame.Rect(cx0, cy0, cell_w, cell_h)
        pygame.draw.rect(sheet, (132, 184, 222), cell, border_radius=14)
        pygame.draw.rect(sheet, (90, 140, 190), cell, 2, border_radius=14)
        sheet.blit(tile, tile.get_rect(center=(cell.centerx, cy0 + 12 + DH // 2)))
        capimg = cap_f.render(cap, True, (24, 26, 64))
        sheet.blit(capimg, capimg.get_rect(midbottom=(cell.centerx, cell.bottom - 11)))

    out = "/home/user/skybit/docs/ghost_label/round_2.png"
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
