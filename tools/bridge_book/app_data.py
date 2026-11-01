"""Print the exercises as a JS array for index.html (CLAR_BRIDGE): [section, title, note, abc], 5 bars per line."""
import json, re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
EX = json.load(open(os.path.join(here, 'ex.json')))
def rebar(abc, per=5):
    lines = abc.strip().split('\n'); head = [l for l in lines if re.match(r'^[A-Z]:', l)]
    body = ' '.join(l for l in lines if not re.match(r'^[A-Z]:', l))
    bars = [b.strip() for b in re.split(r'\|\]|\|', body) if b.strip()]
    rows = [' | '.join(bars[i:i + per]) for i in range(0, len(bars), per)]
    return '\n'.join(h for h in head if not h.startswith('X:')) + '\n' + ' |\n'.join(rows) + ' |]', len(bars)
out = []
for sec, title, note, abc in EX:
    a, n = rebar(abc); out.append([sec.split('. ', 1)[1], title, note, a]); print(title, n, 'bars', file=sys.stderr)
print('const CLAR_BRIDGE = ' + json.dumps(out, ensure_ascii=False) + ';')
