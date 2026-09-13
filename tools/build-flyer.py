#!/usr/bin/env python3
"""Assemble flyer.html from the template, the traced line art and the access map.

    python3 tools/extract-art.py      # (re)creates assets/flyer-art.json
    python3 tools/build-flyer.py      # writes flyer.html

Everything is inlined so the flyer is a single file that prints straight from the
browser (A4, no margins, "background graphics" on).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = json.loads((ROOT / 'assets' / 'flyer-art.json').read_text())


def art(name, extra=''):
    """One traced piece of the original artwork as an inline <svg>."""
    a = ART[name]
    return (f'<svg class="art" viewBox="0 0 {a["w"]} {a["h"]}"{extra} '
            f'preserveAspectRatio="xMidYMid meet">'
            f'<path fill="currentColor" fill-rule="evenodd" d="{a["d"]}"/></svg>')


def svg_file(name):
    return (ROOT / 'tools' / name).read_text().split('?>')[-1].strip()


html = (ROOT / 'tools' / 'flyer.template.html').read_text()
for key in ('header', 'bottom', 'note_l', 'note_r', 'divider',
            'leaf_l', 'leaf_r', 'icon_keys', 'icon_clock', 'icon_door'):
    html = html.replace('{{%s}}' % key, art(key))
html = html.replace('{{map}}', svg_file('access-map.svg'))
html = html.replace('{{qr}}', svg_file('maps-qr.svg'))

out = ROOT / 'flyer.html'
out.write_text(html)
print(f'wrote {out} ({len(html) / 1024:.0f} KB)')
