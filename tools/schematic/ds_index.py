"""Refresh datasheets/README.md parts table from the schematics: refs per LCSC, drop unused rows, add new parts.
usage: python ds_index.py <project_dir>"""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kisexp import *
P = sys.argv[1]
parts = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(P, '*.kicad_sch'))):
    t = parse(open(f, encoding='utf8').read())
    for s in find(t, 'symbol'):
        d = {p[1]: str(p[2]) for p in find(s, 'property')}
        if d['Reference'].startswith('#') or one(s, 'in_bom')[1] != 'yes' or not d.get('LCSC'): continue
        e = parts.setdefault(d['LCSC'], dict(refs=set(), Value=d['Value'], MPN=d.get('MPN', ''), Man=d.get('Manufacturer', '')))
        e['refs'].add(d['Reference'])
def key(r): m = re.match(r'(.*?)(\d*)$', r); return (m.group(1), int(m.group(2) or 0))
TYPE = {'C': 'Capacitors', 'R': 'Resistors', 'L': 'Inductors', 'FB': 'Inductors', 'FL': 'Inductors', 'D': 'Diodes', 'U': 'ICs',
        'Q': 'Transistors', 'K': 'Relays', 'RT': 'Resistors', 'J': 'Connectors', 'TP': 'Connectors', 'SW': 'Connectors', 'Y': 'Crystals', 'F': 'Fuses'}
f = os.path.join(P, 'datasheets', 'README.md')
if not os.path.exists(f): sys.exit(f'{f} not found: create the datasheets index first (instruction.md section 13), then run this again')
src = open(f, encoding='utf8', newline='').read(); nl = '\r\n' if '\r\n' in src else '\n'
lines = src.split(nl); out = []; seen = set()
for l in lines:
    m = re.search(r'\[(C\d+)\]\(https://jlcpcb\.com/partdetail/\1\)', l)
    if l.startswith('| ') and m:
        c = m.group(1)
        if c not in parts: print('drop row', c); continue
        cols = l.split(' | ')
        cols[1] = ', '.join(sorted(parts[c]['refs'], key=key)); seen.add(c)
        cols[2], cols[3], cols[4] = parts[c]['Value'], parts[c]['MPN'], parts[c]['Man']
        l = ' | '.join(cols)
    out.append(l)
CAT = {}   # optional: manufacturer name -> markdown link to a shared catalogue PDF kept in this project's datasheets/ folder
last = max(i for i, l in enumerate(out) if l.startswith('| ') and 'partdetail' in l)
for c, e in parts.items():
    if c in seen: continue
    refs = sorted(e['refs'], key=key); typ = TYPE.get(re.match(r'[A-Z]+', refs[0]).group(0), 'Other')
    fl = CAT.get(e['Man'], f'[JLCPCB Datasheet](https://jlcpcb.com/partdetail/{c})')
    row = f"| {typ} | {', '.join(refs)} | {e['Value']} | {e['MPN']} | {e['Man']} | [{c}](https://jlcpcb.com/partdetail/{c}) | {fl} |"
    last += 1; out.insert(last, row); print('add row', c, refs)
txt = nl.join(out)
txt = re.sub(r'\(\d+ LCSC parts,', '(%d LCSC parts,' % len(parts), txt, count=1)
open(f, 'w', encoding='utf8', newline='').write(txt)
print(len(parts), 'LCSC parts')
