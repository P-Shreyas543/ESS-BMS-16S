"""Pre-flight check for an agent working on a KiCad hardware project.
usage: python tools/check_env.py [project_dir]
Checks: Python, kicad-cli (version), Python packages, headless browser for renders, git, KiCad running / lock files,
project files (lib tables point at existing project libraries). Prints what is missing and how to install it.
Exit code 0 = everything needed is present."""
import os, sys, glob, shutil, subprocess, importlib.util, platform

ok = True
def row(name, good, info='', fix=''):
    global ok
    ok &= bool(good) or name.startswith('(opt)')
    print(f"[{'OK ' if good else 'MISS'}] {name:28s} {info}" + (f"\n       -> {fix}" if not good and fix else ''))

# Python
row('python >= 3.10', sys.version_info >= (3, 10), platform.python_version(), 'install Python 3.10+ from python.org')

# kicad-cli
def find_kicad_cli():
    if os.environ.get('KICAD_CLI') and os.path.exists(os.environ['KICAD_CLI']): return os.environ['KICAD_CLI']
    pats = [os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'KiCad', '*', 'bin', 'kicad-cli.exe'),
            r'C:\Program Files\KiCad\*\bin\kicad-cli.exe',
            '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli']
    for p in pats:
        hits = sorted(glob.glob(p))
        if hits: return hits[-1]
    return shutil.which('kicad-cli')
K = find_kicad_cli(); ver = ''
if K:
    try: ver = subprocess.run([K, 'version'], capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e: ver = f'error {e}'
row('kicad-cli', K, f'{K}  v{ver}', 'install KiCad 10 (kicad.org) or set KICAD_CLI=<path to kicad-cli>')

# python packages
for mod, pipname, why in (('pypdf', 'pypdf', 'read datasheet PDFs'),
                          ('easyeda2kicad', 'easyeda2kicad', 'download LCSC/EasyEDA symbol+footprint+3D for parts not in KiCad')):
    row(f'python: {mod}', importlib.util.find_spec(mod), why, f'python -m pip install {pipname}')

# browser for render.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schematic'))
br = None
for c in (os.environ.get('RENDER_BROWSER', ''), r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
          r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe',
          '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
    if c and os.path.exists(c): br = c; break
br = br or next((shutil.which(n) for n in ('msedge', 'google-chrome', 'chromium', 'chrome') if shutil.which(n)), None)
row('headless browser', br, br or '', 'install Edge or Chrome, or set RENDER_BROWSER=<path> (needed by tools/schematic/render.py)')

row('(opt) git', shutil.which('git'), shutil.which('git') or '', 'install git (only needed if the project is a repo)')

# KiCad running?
try:
    if os.name == 'nt': out = subprocess.run(['tasklist'], capture_output=True, text=True).stdout.lower()
    else: out = subprocess.run(['ps', '-A'], capture_output=True, text=True).stdout.lower()
    running = [n for n in ('kicad', 'eeschema', 'pcbnew') if n in out]
except Exception: running = []
row('KiCad closed', not running, 'running: ' + ', '.join(running) if running else '',
    'ask the owner to save and close KiCad before any file edit')

# project checks
D = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
pro = glob.glob(os.path.join(D, '*.kicad_pro'))
if pro:
    print(f'\nproject: {pro[0]}')
    lck = glob.glob(os.path.join(D, '~*.lck')) + glob.glob(os.path.join(D, '*.lck'))
    row('no lock files', not lck, ' '.join(os.path.basename(x) for x in lck), 'KiCad open (or stale lock after a crash: confirm with the owner)')
    for tab in ('sym-lib-table', 'fp-lib-table'):
        p = os.path.join(D, tab)
        if not os.path.exists(p): row(tab, True, 'none (only global libraries)'); continue
        import re
        uris = re.findall(r'\(uri "([^"]+)"\)', open(p, encoding='utf8').read())
        bad = [u for u in uris if '${KIPRJMOD}' in u and not os.path.exists(u.replace('${KIPRJMOD}', D))]
        row(tab, not bad, f'{len(uris)} libraries' + (f', missing: {bad}' if bad else ''), 'fix the uri or restore the library folder')
    for f in ('PROJECT.md',):
        row(f'(opt) {f}', os.path.exists(os.path.join(D, f)), '', 'create it from instruction.md section 3 before editing')
print('\nMCP / connectors: list your tools. Needed: web search + fetch (JLC/LCSC/datasheet checks).'
      ' Useful: a browser-automation tool (JS-heavy JLC pages), BoardRepo (published reference designs, DRC/ERC, fab limits),'
      ' a file connector (Google Drive) for owner datasheets. Missing ones: tell the owner which and why (Claude Code: /mcp, /plugin).')
print('\nRESULT:', 'ready' if ok else 'missing items above')
sys.exit(0 if ok else 1)
