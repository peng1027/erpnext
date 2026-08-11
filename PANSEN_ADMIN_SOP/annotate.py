#!/usr/bin/env python3
"""
Annotate Pansen VMS admin SOP screenshots with clear callout markers.

Callout style for maximum legibility at print size:
  - a soft highlight ring around the target element (draws the eye)
  - a bold numbered badge with a drop shadow and thick white halo
  - high contrast on any background

Coordinates are fractional (0-1) of each image. The team-management capture is
masked to replace the sample row's tenant text with a generic placeholder.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

SRC = Path(__file__).parent / "raw"
DST = Path(__file__).parent / "annotated"
DST.mkdir(exist_ok=True)

FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_REG = "/System/Library/Fonts/HelveticaNeue.ttc"

RED = (220, 38, 38, 255)
RED_DK = (140, 14, 14, 255)
WHITE = (255, 255, 255, 255)
HL = (255, 210, 0, 70)       # soft yellow highlight (translucent)
HL_RING = (255, 180, 0, 230) # highlight ring
DARK = (31, 41, 55, 255)
GREY = (107, 114, 128, 255)


def _badge(base, marks, W, H, radius_pct=0.0145, highlight=True):
    radius = int(W * radius_pct)
    font_num = ImageFont.truetype(FONT_BOLD, int(radius * 1.4))

    # --- layer 1: soft highlight ring around each target (under the badge) ---
    if highlight:
        hl = Image.new("RGBA", base.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        hr = int(radius * 1.4)
        for m in marks:
            cx, cy = int(W * m["x"]), int(H * m["y"])
            hd.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=HL)
            hd.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], outline=HL_RING, width=max(3, radius // 8))
        hl = hl.filter(ImageFilter.GaussianBlur(radius * 0.12))
        base.alpha_composite(hl)

    # --- layer 2: drop shadow ---
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    off = max(3, radius // 6)
    for m in marks:
        cx, cy = int(W * m["x"]) + off, int(H * m["y"]) + off
        sd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(radius * 0.18))
    base.alpha_composite(sh)

    # --- layer 3: badge (white halo + red circle + number) ---
    bd = ImageDraw.Draw(base)
    for m in marks:
        cx, cy = int(W * m["x"]), int(H * m["y"])
        halo = radius + max(4, radius // 4)
        bd.ellipse([cx - halo, cy - halo, cx + halo, cy + halo], fill=WHITE)
        bd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                   fill=RED, outline=RED_DK, width=max(3, radius // 10))
        num = str(m["n"])
        b = bd.textbbox((0, 0), num, font=font_num)
        tw, th = b[2] - b[0], b[3] - b[1]
        bd.text((cx - tw / 2 - b[0], cy - th / 2 - b[1]), num, font=font_num, fill=WHITE)


def annotate(src_name, marks, pre_mask=None, **kw):
    img = Image.open(SRC / src_name).convert("RGBA")
    W, H = img.size
    if pre_mask:
        pre_mask(img, ImageDraw.Draw(img), W, H)
    _badge(img, marks, W, H, **kw)
    out = img.convert("RGB")
    out_name = src_name.replace(".png", "_annotated.png")
    out.save(DST / out_name, "PNG", optimize=True)
    print(f"  {out_name}  ({len(marks)} markers)")


def mask_team_management(img, draw, W, H):
    x0, y0, x1, y1 = int(W * 0.227), int(H * 0.385), int(W * 0.43), int(H * 0.45)
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 255))
    name_font = ImageFont.truetype(FONT_BOLD, int(W * 0.013))
    email_font = ImageFont.truetype(FONT_REG, int(W * 0.011))
    draw.text((x0 + 5, y0 + 5), "Site Administrator", font=name_font, fill=DARK)
    draw.text((x0 + 5, y0 + int(H * 0.028)), "admin@your-site.com", font=email_font, fill=GREY)


print("Annotating (callout style)...")

annotate("vms_sop_01_login.png", [
    {"n": 1, "x": 0.50, "y": 0.395}, {"n": 2, "x": 0.50, "y": 0.475},
    {"n": 3, "x": 0.565, "y": 0.530}, {"n": 4, "x": 0.50, "y": 0.585},
])
annotate("vms_sop_02_dashboard.png", [
    {"n": 1, "x": 0.30, "y": 0.41}, {"n": 2, "x": 0.275, "y": 0.555},
    {"n": 3, "x": 0.30, "y": 0.705}, {"n": 4, "x": 0.285, "y": 0.855},
    {"n": 5, "x": 0.34, "y": 0.935},
])
annotate("site_pass_list.png", [
    {"n": 1, "x": 0.823, "y": 0.082}, {"n": 2, "x": 0.703, "y": 0.082},
    {"n": 3, "x": 0.135, "y": 0.165}, {"n": 4, "x": 0.515, "y": 0.144},
])
annotate("site_pass_form.png", [
    {"n": 1, "x": 0.22, "y": 0.225}, {"n": 2, "x": 0.22, "y": 0.32},
    {"n": 3, "x": 0.22, "y": 0.405}, {"n": 4, "x": 0.665, "y": 0.32},
    {"n": 5, "x": 0.835, "y": 0.075},
])
annotate("self_registration.png", [
    {"n": 1, "x": 0.50, "y": 0.105}, {"n": 2, "x": 0.41, "y": 0.215},
    {"n": 3, "x": 0.43, "y": 0.305}, {"n": 4, "x": 0.605, "y": 0.490},
    {"n": 5, "x": 0.605, "y": 0.590},
])
annotate("security_scanner_main.png", [
    {"n": 1, "x": 0.420, "y": 0.200}, {"n": 2, "x": 0.500, "y": 0.300},
    {"n": 3, "x": 0.435, "y": 0.460}, {"n": 4, "x": 0.565, "y": 0.460},
    {"n": 5, "x": 0.475, "y": 0.625},
])
annotate("team_management.png", [
    {"n": 1, "x": 0.275, "y": 0.22}, {"n": 2, "x": 0.825, "y": 0.10},
    {"n": 3, "x": 0.710, "y": 0.10}, {"n": 4, "x": 0.275, "y": 0.31},
    {"n": 5, "x": 0.940, "y": 0.41},
], pre_mask=mask_team_management)
annotate("vms_site_pass_report.png", [
    {"n": 1, "x": 0.20, "y": 0.225}, {"n": 2, "x": 0.42, "y": 0.225},
    {"n": 3, "x": 0.81, "y": 0.225}, {"n": 4, "x": 0.83, "y": 0.105},
])

# --- Worker registration (captured from the live public form, nothing submitted) ---
annotate("worker_type_select.png", [
    {"n": 1, "x": 0.559, "y": 0.372},   # Worker tab (Contractor / Labor)
    {"n": 2, "x": 0.527, "y": 0.555},   # Verify with Aadhaar
    {"n": 3, "x": 0.481, "y": 0.742},   # Camera (photo is required)
    {"n": 4, "x": 0.499, "y": 0.860},   # Full Name
])
# Marker 4 is the End Date, called out deliberately: it is the one
# optional-looking field that silently changes how long the pass lives. Left
# blank, the worker gets 30 days instead of the job's real end date.
annotate("worker_form.png", [
    {"n": 1, "x": 0.591, "y": 0.441},   # Mobile + OTP
    {"n": 2, "x": 0.499, "y": 0.643},   # Contractor Company (required)
    {"n": 3, "x": 0.440, "y": 0.745},   # Start Date (required)
    {"n": 4, "x": 0.559, "y": 0.746},   # End Date  <- the 30-day trap
    {"n": 5, "x": 0.499, "y": 0.851},   # Work Description
])

print("Done.")
