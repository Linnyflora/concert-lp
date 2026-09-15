"""印章らしい印影をつくる。
朱肉の色（朱色）、押しムラによる濃淡、ふちのかすれ、細かい白抜けを重ねる。"""
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 1200                 # 作業解像度
OUT = 420                # 書き出し

# 印影の書体は Shippori Mincho B1 ExtraBold（SIL OFL）。
# 明朝の太いウエイトなので、印鑑の書体に近い見え方になる。
FONT_URL = ('https://raw.githubusercontent.com/google/fonts/main/ofl/'
            'shipporiminchob1/ShipporiMinchoB1-ExtraBold.ttf')
FB1 = (pathlib.Path(__file__).resolve().parent.parent
       / 'assets' / 'fonts' / 'ShipporiMinchoB1-ExtraBold.ttf')


def _font():
    """書体がなければ取ってくる（.ttf はリポジトリに入れていないため）。"""
    if not FB1.exists():
        import urllib.request
        FB1.parent.mkdir(parents=True, exist_ok=True)
        print('downloading', FONT_URL)
        urllib.request.urlretrieve(FONT_URL, FB1)
    return str(FB1)

# 朱肉の色。濃いところは深い朱、薄いところは橙寄りになるよう2色を混ぜる
# 朱肉の色。濃いところは深い朱、薄いところは橙寄りになるよう2色を混ぜる
INK_DEEP  = np.array([198, 38, 28], float)    # 深い朱
INK_LIGHT = np.array([232, 96, 58], float)    # 薄いところ（橙寄り）


def _noise(shape_div, seed, size=S):
    """なめらかな雲状のノイズ（0〜1）。"""
    rng = np.random.default_rng(seed)
    n = rng.random((max(2, size // shape_div), max(2, size // shape_div)))
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
    a = np.array(im.filter(ImageFilter.GaussianBlur(size / 120)), float) / 255
    return (a - a.min()) / max(1e-6, np.ptp(a))


def impress(mask, seed=3):
    """マスク（白=朱が乗る）→ 朱色の印影 RGBA。"""
    # ふちを少しにじませる
    mask = mask.filter(ImageFilter.GaussianBlur(S / 700))
    a = np.array(mask, float) / 255

    rng = np.random.default_rng(seed)

    # 1) 押しムラ。斜めの勾配で片側をわずかに薄く（手で押したときの陰影）
    yy, xx = np.mgrid[0:S, 0:S] / S
    ang = rng.uniform(0, 2 * np.pi)
    g = np.cos(ang) * xx + np.sin(ang) * yy
    g = (g - g.min()) / np.ptp(g)
    a *= 0.80 + 0.26 * g

    # 2) 大きなムラ＋中くらいのムラ（朱肉の乗り方の濃淡）
    a *= 0.80 + 0.32 * _noise(14, seed + 1)
    a *= 0.86 + 0.22 * _noise(5, seed + 2)

    # 3) かすれ。ところどころ朱肉が乗りきらずに霞む
    k = _noise(3, seed + 3)
    a *= np.where(k < 0.26, 0.40 + 2.2 * k, 1.0)

    # 4) 細かい白抜け（朱肉の粒）
    fine = rng.random((S, S))
    a *= np.where(fine > 0.965, 0.30, 1.0)

    # 全体はしっかり朱が乗っている状態に持ち上げる
    a = np.clip(a * 1.14, 0, 1) ** 0.90
    a = np.array(Image.fromarray((a * 255).astype(np.uint8))
                 .filter(ImageFilter.GaussianBlur(S / 900)), float) / 255

    # 5) 色。濃いところは深い朱、薄いところは橙寄り＝陰影が出る
    t = np.clip((a - 0.30) / 0.58, 0, 1)[..., None]
    rgb = INK_LIGHT * (1 - t) + INK_DEEP * t

    out = np.dstack([rgb, np.clip(a * 253, 0, 255)]).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    # ほんのわずかに傾ける（手押しらしさ）
    im = im.rotate(rng.uniform(-1.6, 1.6), resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    im = im.resize((OUT, OUT), Image.LANCZOS)
    # Apps Script には base64 で埋め込むので、見た目を保ったまま軽くする
    return im.quantize(colors=64, method=Image.FASTOCTREE)


def _fit(d, box, text, start=520):
    size = start
    while size > 8:
        f = ImageFont.truetype(_font(), size)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        if r - l <= box[0] and b - t <= box[1]:
            return f
        size -= 4
    return ImageFont.truetype(_font(), 12)


def circle_two(top, bottom, ring=34, inner=True, seed=3):
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    pad = 30
    d.ellipse([pad, pad, S - pad, S - pad], outline=255, width=ring)
    if inner:
        g = pad + ring + 34
        d.ellipse([g, g, S - g, S - g], outline=255, width=max(10, ring // 3))
    half = (S - 2 * (pad + ring + 80)) // 2
    for i, ch in enumerate((top, bottom)):
        f = _fit(d, (half * 2 - 26, half - 26), ch)
        l, t, r, b = d.textbbox((0, 0), ch, font=f)
        cy = S // 2 + (-1 if i == 0 else 1) * (half // 2 + 10)
        d.text((S // 2 - (r + l) / 2, cy - (b + t) / 2), ch, font=f, fill=255)
    return impress(m, seed)


def square_four(chars, ring=40, seed=3):
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    pad = 54
    d.rounded_rectangle([pad, pad, S - pad, S - pad], radius=22, outline=255, width=ring)
    ip = pad + ring + 44
    cell = (S - 2 * ip) / 2
    for ch, (col, row) in zip(chars, [(1, 0), (1, 1), (0, 0), (0, 1)]):
        f = _fit(d, (cell - 16, cell - 16), ch)
        l, t, r, b = d.textbbox((0, 0), ch, font=f)
        d.text((ip + cell * (col + .5) - (r + l) / 2,
                ip + cell * (row + .5) - (b + t) / 2), ch, font=f, fill=255)
    return impress(m, seed)


def from_photo(path, seed=11):
    """いただいた実物の印鑑の写真から、同じ質感で刷り直す。"""
    im = Image.open(path).convert('RGB').resize((S, S), Image.LANCZOS)
    a = np.array(im, float)
    # 赤い（＝朱肉の）ところを拾う
    ink = np.clip((a[..., 1] + a[..., 2]) / 2, 0, 255)
    m = np.clip((235 - ink) / 150, 0, 1) * 255
    return impress(Image.fromarray(m.astype(np.uint8)), seed)


if __name__ == '__main__':
    root = pathlib.Path(__file__).resolve().parent.parent
    opts = root / 'assets' / 'seal-options'
    opts.mkdir(exist_ok=True)

    a = from_photo(root / 'assets' / 'seal-source.png')
    a.save(opts / 'a-maru-masumi.png')
    a.save(root / 'assets' / 'seal.png')                  # 領収証に入っているもの
    circle_two('増', '見', seed=3).save(opts / 'b-maru-masumi-mincho.png')
    circle_two('麻', '美', inner=False, ring=38, seed=5).save(opts / 'c-maru-asami.png')
    square_four('増見麻美', seed=7).save(opts / 'd-kaku-masumiasami.png')
    square_four('増見之印', seed=9).save(opts / 'e-kaku-masumi-no-in.png')
    print('wrote', opts)
