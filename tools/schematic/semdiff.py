import sys
from kisexp import *
def load(f): return parse(open(f,encoding='utf8').read())
a=load(sys.argv[1]); b=load(sys.argv[2])
def syms(t):
    r={}
    for s in find(t,'symbol'):
        p={x[1]:(x[2], one(x,'at')[1:], bool(one(x,'hide')), (one(one(x,'effects'),'justify') or [])[1:]) for x in find(s,'property')}
        r[p['Reference'][0]]=(one(s,'at')[1:],one(s,'lib_id')[1],p)
    return r
A,B=syms(a),syms(b)
print('only in A',sorted(set(A)-set(B)),'only in B',sorted(set(B)-set(A)))
for ref in sorted(set(A)&set(B)):
    (aa,la,pa),(ab,lb,pb)=A[ref],B[ref]; d=[]
    if aa!=ab: d.append(f'pos {aa}->{ab}')
    if la!=lb: d.append(f'lib {la}->{lb}')
    for k in sorted(set(pa)|set(pb)):
        if pa.get(k)!=pb.get(k): d.append(f'{k}: {pa.get(k)} -> {pb.get(k)}')
    if d: print(ref); [print('   ',x) for x in d]
for k in ('text','label','hierarchical_label','wire','junction','rectangle','no_connect'):
    ka=sorted(dump([c for c in x if not (isinstance(c,list) and c and c[0]=='uuid')]) for x in find(a,k))
    kb=sorted(dump([c for c in x if not (isinstance(c,list) and c and c[0]=='uuid')]) for x in find(b,k))
    if ka!=kb: print(k, len(ka),'->',len(kb),'DIFFER'); [print('   -',x.replace(chr(10),' ')[:160]) for x in sorted(set(ka)-set(kb))[:8]]; [print('   +',x.replace(chr(10),' ')[:160]) for x in sorted(set(kb)-set(ka))[:8]]
print('paper', one(a,'paper'), one(b,'paper'))
