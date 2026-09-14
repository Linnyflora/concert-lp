"""クレヨン塗りのカラーレイヤーをつくる。

線画は開いた形（塗りつぶしが外へ漏れる）なので、手で置いた色パッチに
・ムラのあるノイズ
・斜めのストローク
・輪郭のゆらぎ（線からわずかにはみ出す）
を掛けて、クレヨンで塗ったように見せる。
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def norm(a):
    return (a - a.min()) / (np.ptp(a) + 1e-9)


def crayon_texture(W, H, seed=0, angle=0.6):
    """紙の目 + 斜めのストロークによる濃淡（0.35〜1.0）"""
    rng = np.random.default_rng(seed)
    small = (rng.random((max(H // 6, 2), max(W // 6, 2))) * 255).astype(np.uint8)
    grain = np.asarray(Image.fromarray(small).resize((W, H), Image.BILINEAR), dtype=np.float32)
    grain = norm(ndimage.gaussian_filter(grain, 2.5))
    yy, xx = np.mgrid[0:H, 0:W]
    wobble = ndimage.gaussian_filter(rng.random((H, W)), 14) * 26
    streak = 0.5 + 0.5 * np.sin((xx * np.cos(angle) + yy * np.sin(angle)) * 0.30 + wobble)
    streak = ndimage.gaussian_filter(streak, 1.2)
    tex = 0.34 + 0.66 * (0.42 * grain + 0.58 * streak)
    return np.clip(tex, 0, 1)


def wobble_mask(mask, seed=0, amp=5.0, smooth=26):
    """輪郭をゆらして手塗りらしく（線からはみ出したり、届かなかったり）"""
    H, W = mask.shape
    rng = np.random.default_rng(seed + 991)
    dy = ndimage.gaussian_filter(rng.random((H, W)) - 0.5, smooth) * amp * smooth
    dx = ndimage.gaussian_filter(rng.random((H, W)) - 0.5, smooth) * amp * smooth
    yy, xx = np.mgrid[0:H, 0:W]
    out = ndimage.map_coordinates(mask.astype(np.float32), [yy + dy, xx + dx], order=1)
    return np.clip(out, 0, 1)


class CrayonLayer:
    """色パッチを重ねてクレヨン風のRGBAレイヤーをつくる"""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.rgb = np.zeros((H, W, 3), dtype=np.float32)
        self.alpha = np.zeros((H, W), dtype=np.float32)
        self.n = 0

    def _shape_mask(self, draw_fn):
        img = Image.new('L', (self.W, self.H), 0)
        draw_fn(ImageDraw.Draw(img))
        return np.array(img, dtype=np.float32) / 255.0

    def patch(self, draw_fn, color, strength=0.85, blur=3.0, amp=4.0, angle=0.6):
        m = self._shape_mask(draw_fn)
        m = wobble_mask(m, seed=self.n, amp=amp)
        m = ndimage.gaussian_filter(m, blur)
        tex = crayon_texture(self.W, self.H, seed=self.n * 7 + 3, angle=angle)
        a = np.clip(m * tex * strength, 0, 1)
        col = np.array(color, dtype=np.float32) / 255.0
        # 後から塗った色を上に重ねる
        self.rgb = self.rgb * (1 - a)[..., None] + col * a[..., None]
        self.alpha = np.clip(self.alpha + a * (1 - self.alpha), 0, 1)
        self.n += 1

    def ellipse(self, cx, cy, rx, ry, color, **kw):
        self.patch(lambda d: d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255), color, **kw)

    def poly(self, pts, color, **kw):
        self.patch(lambda d: d.polygon(pts, fill=255), color, **kw)

    def rect(self, x0, y0, x1, y1, color, **kw):
        self.patch(lambda d: d.rectangle([x0, y0, x1, y1], fill=255), color, **kw)

    def mask(self, bool_mask, color, **kw):
        m = bool_mask.astype(np.float32)
        m = wobble_mask(m, seed=self.n, amp=kw.get('amp', 2.5))
        m = ndimage.gaussian_filter(m, kw.get('blur', 2.0))
        tex = crayon_texture(self.W, self.H, seed=self.n * 7 + 3, angle=kw.get('angle', 0.6))
        a = np.clip(m * tex * kw.get('strength', 0.85), 0, 1)
        col = np.array(color, dtype=np.float32) / 255.0
        self.rgb = self.rgb * (1 - a)[..., None] + col * a[..., None]
        self.alpha = np.clip(self.alpha + a * (1 - self.alpha), 0, 1)
        self.n += 1

    def image(self):
        rgba = np.zeros((self.H, self.W, 4), dtype=np.uint8)
        rgba[..., :3] = np.clip(self.rgb * 255, 0, 255).astype(np.uint8)
        rgba[..., 3] = np.clip(self.alpha * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(rgba, 'RGBA')


def preview(color_img, lines_path, out, paper=(250, 248, 246), size=None):
    """紙 → 色 → 線 の順に重ねた確認用画像"""
    lines = Image.open(lines_path).convert('L')
    W, H = lines.size
    base = Image.new('RGB', (W, H), paper)
    base.paste(color_img, (0, 0), color_img)
    ink = Image.fromarray(255 - np.array(lines)).convert('L')
    base.paste(Image.new('RGB', (W, H), (47, 43, 40)), (0, 0), ink)
    if size:
        base = base.resize(size, Image.LANCZOS)
    base.save(out)
    return base
