"""Absolute pin-tip positions of symbol instances in a KiCad schematic.
pin (px, py) in the lib -> (X, Y) + R(rot) . (px, -py); mirror not handled (asserted absent)."""
import math
from kisexp import *

def f(v): return round(float(v), 3)

def lib_pins(t):
    out = {}
    for ls in find(one(t, 'lib_symbols'), 'symbol'):
        name = ls[1]; pins = []
        for sub in find(ls, 'symbol'):
            # sub-symbol name ends with _<unit>_<style>
            unit = int(sub[1].rsplit('_', 2)[-2])
            for p in find(sub, 'pin'):
                a = one(p, 'at'); ln = one(p, 'length')
                pins.append(dict(num=one(p, 'number')[1], name=one(p, 'name')[1], unit=unit,
                                 x=f(a[1]), y=f(a[2]), ang=f(a[3]) if len(a) > 3 else 0.0,
                                 length=f(ln[1]) if ln else 0.0, etype=p[1]))
        out[name] = pins
    return out

def inst_pins(t, s, LP=None):
    LP = LP or lib_pins(t)
    lib = one(s, 'lib_id')[1]; a = one(s, 'at'); X, Y = f(a[1]), f(a[2]); rot = f(a[3]) if len(a) > 3 else 0
    assert not one(s, 'mirror'), 'mirror not supported'
    unit = int(one(s, 'unit')[1]) if one(s, 'unit') else 1
    r = math.radians(rot); c, sn = round(math.cos(r)), -round(math.sin(r))   # KiCad rotates CCW on screen (y down)
    res = []
    for p in LP[lib]:
        if p['unit'] not in (0, unit): continue
        px, py = p['x'], -p['y']
        res.append(dict(p, X=round(X + c * px - sn * py, 3), Y=round(Y + sn * px + c * py, 3)))
    return res
