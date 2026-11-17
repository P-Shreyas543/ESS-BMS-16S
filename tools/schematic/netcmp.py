"""Compare connectivity of two KiCad netlists (kicadsexpr), ignoring net names.
usage: python netcmp.py before.net after.net
Exit code 0 = identical connectivity, 1 = different (differences printed)."""
import sys
from kisexp import parse, find, one

def nets(path):
    n = parse(open(path, encoding='utf8').read())
    out = {}
    for net in find(one(n, 'nets'), 'net'):
        nodes = tuple(sorted((one(x, 'ref')[1], one(x, 'pin')[1]) for x in find(net, 'node')))
        out[nodes] = one(net, 'name')[1]
    return out

a, b = nets(sys.argv[1]), nets(sys.argv[2])
same = set(a) == set(b)
print('connectivity identical:', same)
renamed = {a[k]: b[k] for k in set(a) & set(b) if a[k] != b[k]}
if renamed:
    print('renamed nets (expected when labels become global symbols):')
    for old, new in sorted(renamed.items()):
        print('   ', old, '->', new)
for k in sorted(set(a) - set(b)):
    print('ONLY BEFORE:', a[k], k)
for k in sorted(set(b) - set(a)):
    print('ONLY AFTER :', b[k], k)
sys.exit(0 if same else 1)
