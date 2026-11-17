"""Summarise a kicad-cli ERC report per sheet.
usage: python ercsum.py erc.rpt [sheet-substring]
Prints error/warning counts by type for every sheet; with a sheet substring also prints that sheet's full entries."""
import sys, re, collections

t = open(sys.argv[1], encoding='utf8').read()
sel = sys.argv[2] if len(sys.argv) > 2 else None
for sh in re.findall(r'\*\*\*\*\* Sheet ([^\n]+)', t):
    i = t.find('***** Sheet ' + sh); j = t.find('*****', i + 10); s = t[i:j if j > 0 else None]
    c = collections.Counter(re.findall(r'\[(\w+)\]: [^\n]*\n\s+; (error|warning)', s))
    e = sum(v for (k, sev), v in c.items() if sev == 'error'); w = sum(v for (k, sev), v in c.items() if sev == 'warning')
    print(f'{sh:34s} errors {e:3d}  warnings {w:3d}  ', dict(c))
    if sel and sel in sh:
        print(s)
