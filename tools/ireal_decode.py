"""Decode iReal Pro share links (irealb:// and irealbook://) found in saved forum pages.

Download a thread first, e.g.  curl -sL -o /tmp/t.html https://forums.irealpro.com/threads/<thread>/
Then:                           python3 tools/ireal_decode.py /tmp/t.html -- mohawk
Prints each matching chart (concert pitch) as bars. See tools/add_chart.py to add one to library.json.
"""
import re, html, urllib.parse, glob, json, sys

def obfusc50(s):
    n = list(s)
    for i in range(5): n[49 - i] = s[i]; n[i] = s[49 - i]
    for i in range(10, 24): n[49 - i] = s[i]; n[i] = s[49 - i]
    return ''.join(n)
def unscramble(s):
    r = ''
    while len(s) > 51: r += obfusc50(s[:50]); s = s[50:]
    r += s
    return r.replace('Kcl', '| x').replace('LZ', ' |').replace('XyQ', '   ')

def songs(files):
    out = []
    for f in files:
        t = open(f, encoding='utf-8', errors='ignore').read()
        for l in re.findall(r'(irealb://[^"\'<\s]+)', t):
            u = urllib.parse.unquote(html.unescape(l))[len('irealb://'):]
            for p in u.split('==='):
                parts = p.split('=')
                music = next((x for x in parts if x.startswith('1r34LbKcu7')), None)
                if not music: continue
                out.append({'title': parts[0], 'composer': parts[1], 'style': parts[3], 'key': parts[4], 'music': unscramble(music[len('1r34LbKcu7'):]), 'src': f})
        for l in re.findall(r'(irealbook://[^"\'<\s]+)', t):
            u = urllib.parse.unquote(html.unescape(l))[len('irealbook://'):]
            parts = u.split('=')
            if len(parts) >= 6: out.append({'title': parts[0], 'composer': parts[1], 'style': parts[2], 'key': parts[3], 'music': parts[5], 'src': f + ' (irealbook)'})
    return out

QMAP = [('-^7', 'm(maj7)'), ('-^9', 'm(maj9)'), ('-^', 'm(maj7)'), ('^7', 'maj7'), ('^9', 'maj9'), ('^13', 'maj13'), ('^', 'maj7'), ('h7', 'ø7'), ('h9', 'ø9'), ('h', 'ø7'), ('o7', '°7'), ('o', '°'), ('-', 'm')]
def conv_chord(c):
    m = re.match(r'^([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?$', c)
    if not m: return None
    root, q, bass = m.groups()
    for a, b in QMAP:
        if q.startswith(a): q = b + q[len(a):]; break
    return root + q + ('/' + bass if bass else '')

def parse_music(mu):
    mu = re.sub(r'<[^>]*>', ' ', mu)          # comments
    mu = re.sub(r'\([^)]*\)', ' ', mu)        # alternate chords
    toks = re.findall(r'\*[A-Za-z]|T\d\d|N\d|[|\[\]{}Z]|[A-G][#b]?[^\s|\[\]{}Z,*]*|x|r|n|.', mu)
    bars, cur, pend = [], {'c': []}, {}
    ts = None
    def close(barline):
        nonlocal cur, pend
        if cur['c'] or cur.get('rep'):
            cur['n'] = len(bars) + 1; bars.append(cur)
            if barline == '}': cur['rc'] = 1
        cur = {'c': []}; cur.update(pend); pend = {}
    for t in toks:
        if t in '|[]{}Z':
            close(t)
            if t == '{': cur['ro'] = 1
            continue
        if t.startswith('*') and len(t) > 1: cur['sec'] = {'i': 'Intro', 'V': 'Verse'}.get(t[1], t[1]); continue
        if re.fullmatch(r'T\d\d', t): ts = ts or (t[1] + '/' + t[2]); continue
        if re.fullmatch(r'N\d', t): cur['end'] = int(t[1]); continue
        if t == 'x':
            if bars: cur['c'] = list(bars[-1]['c']); cur['rep'] = 1
            continue
        if t == 'r':
            if len(bars) >= 2:
                cur['c'] = list(bars[-2]['c']); cur['rep'] = 2; close('|'); cur['c'] = list(bars[-2]['c']); cur['rep'] = 1
            continue
        if t == 'n': cur['c'].append('N.C.'); continue
        if re.match(r'[A-G]', t):
            c = conv_chord(t.rstrip('sl*fQSUY'))
            if c: cur['c'].append(c)
    close('|')
    # drop leftover empty bars, renumber
    bars = [b for b in bars if b['c']]
    for i, b in enumerate(bars): b['n'] = i + 1
    return bars, ts or '4/4'

if __name__ == '__main__':
    # usage: python3 tools/ireal_decode.py page1.html [page2.html ...] -- word1 [word2 ...]
    args = sys.argv[1:]; files = args[:args.index('--')] if '--' in args else args; words = args[args.index('--') + 1:] if '--' in args else ['']
    for s in songs(files):
        if any(w.lower() in s['title'].lower() for w in words):
            bars, ts = parse_music(s['music'])
            print('==', s['title'], '|', s['composer'], '|', s['style'], '| key', s['key'], '|', len(bars), 'bars', ts, '|', s['src'].split('/')[-1][2:30])
            print('   raw:', s['music'][:160])
            print('   ', ' | '.join(('[' + b['sec'] + '] ' if b.get('sec') else '') + ('%' if b.get('rep') else ' '.join(b['c'])) for b in bars))
