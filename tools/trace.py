from PIL import Image, ImageDraw
import numpy as np, potrace

def trace_img(img, scale=4, thresh=185, turd=4, alpha=1.0, invert=False):
    w, h = img.size
    big = img.resize((w*scale, h*scale), Image.LANCZOS)
    a = np.array(big)
    # potracer's Bitmap inverts internally: pass the grayscale as-is so that
    # pixels darker than `thresh` end up as the traced foreground.
    bmp = potrace.Bitmap(a, blacklevel=thresh / 255.0)
    path = bmp.trace(turdsize=turd, alphamax=alpha, opticurve=True, opttolerance=0.2)
    parts = []
    for curve in path:
        s = curve.start_point
        d = f"M{s.x:.1f},{s.y:.1f}"
        for seg in curve:
            if seg.is_corner:
                d += f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}"
            else:
                d += (f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} "
                      f"{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        parts.append(d + "Z")
    return w*scale, h*scale, "".join(parts)

def svg(vw, vh, d, cls=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" '
            f'class="{cls}" preserveAspectRatio="xMidYMid meet">'
            f'<path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>')
