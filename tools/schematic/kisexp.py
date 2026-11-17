"""Lossless-enough KiCad s-expression reader/writer (keeps quoted vs bare atoms)."""
import re, uuid as _uuid

class Q(str):
    """quoted string atom"""

TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')

def _unesc(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            out.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(n, '\\' + n)); i += 2
        else:
            out.append(c); i += 1
    return ''.join(out)

def _esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def parse(s):
    stack = [[]]
    for m in TOK.finditer(s):
        t = m.group()
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        elif t[0] == '"':
            stack[-1].append(Q(_unesc(t[1:-1])))
        else:
            stack[-1].append(t)
    return stack[0][0]

def _atom(a):
    return '"' + _esc(a) + '"' if isinstance(a, Q) else str(a)

INLINE = {'at', 'xy', 'size', 'start', 'end', 'mid', 'center', 'radius', 'width', 'type', 'uuid', 'length',
          'offset', 'hide', 'justify', 'thickness', 'bold', 'italic', 'color', 'lib_id', 'unit', 'page',
          'exclude_from_sim', 'in_bom', 'on_board', 'dnp', 'fields_autoplaced', 'diameter', 'version',
          'generator', 'generator_version', 'paper', 'show_name', 'do_not_autoplace', 'in_pos_files',
          'embedded_fonts', 'reference', 'number', 'shape', 'mirror', 'convert', 'body_style', 'name', 'path'}

def dump(n, ind=0):
    if not isinstance(n, list):
        return _atom(n)
    head = n[0]
    simple = all(not isinstance(c, list) for c in n)
    if simple:
        return '(' + ' '.join(_atom(c) for c in n) + ')'
    if head == 'pts':
        return '(pts\n' + '\t' * (ind + 1) + ' '.join(dump(c) for c in n[1:]) + '\n' + '\t' * ind + ')'
    parts = ['(' + _atom(head)]
    i = 1
    while i < len(n) and not isinstance(n[i], list):
        parts[0] += ' ' + _atom(n[i]); i += 1
    body = ''.join('\n' + '\t' * (ind + 1) + dump(c, ind + 1) for c in n[i:])
    return parts[0] + body + '\n' + '\t' * ind + ')'

def find(n, name): return [c for c in n if isinstance(c, list) and c and c[0] == name]
def one(n, name):
    r = find(n, name); return r[0] if r else None
def walk(n):
    if isinstance(n, list):
        yield n
        for c in n:
            yield from walk(c)
def uid(): return Q(str(_uuid.uuid4()))
def num(x):
    s = f'{x:.4f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s
