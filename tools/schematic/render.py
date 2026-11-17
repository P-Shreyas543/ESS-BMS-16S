"""Render a KiCad schematic SVG crop (mm coords) to PNG via headless Edge.
usage: python render.py in.svg out.png x0 y0 x1 y1 [px_per_mm]"""
import sys, re, subprocess, os, pathlib
svg, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(float, sys.argv[3:7])
ppm = float(sys.argv[7]) if len(sys.argv) > 7 else 8
txt = open(svg, encoding='utf8').read()
# kicad svg: width="420.0mm" viewBox="0 0 420000 297000" style units (1/1000 mm) -- detect scale
vb = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.\-]+) ([\d.\-]+)"', txt)
w_mm = float(re.search(r'width="([\d.]+)mm"', txt).group(1))
scale = float(vb.group(3)) / w_mm
nvb = f'{x0*scale} {y0*scale} {(x1-x0)*scale} {(y1-y0)*scale}'
W, H = int((x1 - x0) * ppm), int((y1 - y0) * ppm)
txt = re.sub(r'viewBox="[^"]+"', f'viewBox="{nvb}"', txt, count=1)
txt = re.sub(r'width="[\d.]+mm"', f'width="{W}px"', txt, count=1)
txt = re.sub(r'height="[\d.]+mm"', f'height="{H}px"', txt, count=1)
tmp = pathlib.Path(out).with_suffix('.html')
tmp.write_text('<html><body style="margin:0;background:#fff">' + txt[txt.find('<svg'):] + '</body></html>', encoding='utf8')
def find_browser():
    import shutil
    if os.environ.get('RENDER_BROWSER'): return os.environ['RENDER_BROWSER']
    for c in (r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'):
        if os.path.exists(c): return c
    for n in ('msedge', 'microsoft-edge', 'google-chrome', 'chromium', 'chromium-browser', 'chrome'):
        if shutil.which(n): return shutil.which(n)
    sys.exit('render.py: no headless Edge/Chrome found; set RENDER_BROWSER=<path>')
edge = find_browser()
subprocess.run([edge,'--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={W},{H}',
                f'--screenshot={os.path.abspath(out)}', tmp.resolve().as_uri()], capture_output=True, timeout=120)
print(out, W, H)
