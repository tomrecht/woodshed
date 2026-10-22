"""Add one decoded iReal chart to library.json, converted from concert pitch to an Eb (alto) part.

python3 tools/add_chart.py /tmp/t.html "Source title" "Title in the app" "Composer"
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ireal_decode import songs, parse_music
PCS = {'C':0,'B#':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'Fb':4,'F':5,'E#':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11,'Cb':11}
FL = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']; SH = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
MAJ = ['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']; MIN = ['Cm','C#m','Dm','Ebm','Em','Fm','F#m','Gm','G#m','Am','Bbm','Bm']
def sharp_key(k):
    pc = PCS[k.rstrip('m')]; return pc in ([4,11,6,1,8] if k.endswith('m') else [7,2,9,4,11,6])
def tr(sym, semis, sharp):
    m = re.match(r'^([A-G][#b]?)(.*?)(?:/([A-G][#b]?))?$', sym)
    if not m: return sym
    def sp(n):   # keep the original's accidental direction; naturals follow the key
        nm = SH if ('#' in n or ('b' not in n and sharp)) else FL
        return nm[(PCS[n] + semis) % 12]
    return sp(m[1]) + m[2] + ('/' + sp(m[3]) if m[3] else '')

def main(page, src_title, app_title, composer):
    s = next(x for x in songs([page]) if x['title'] == src_title)
    bars, ts = parse_music(s['music'])
    ck = s['key'].replace('-', 'm')
    ek = (MIN if ck.endswith('m') else MAJ)[(PCS[ck.rstrip('m')] + 9) % 12]
    sh = sharp_key(ek)
    for b in bars: b['c'] = [c if c == 'N.C.' else tr(c, 9, sh) for c in b['c']]
    path = os.path.join(os.path.dirname(__file__), '..', 'library.json')
    lib = [e for e in json.load(open(path)) if e['t'] != app_title]
    lib.append({'t': app_title, 's': s['style'], 'c': composer, 'k': ek, 'ts': ts, 'b': bars, 'src': 'iReal Pro forums'})
    lib.sort(key=lambda e: e['t'].lower())
    json.dump(lib, open(path, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('added', app_title, '| concert', ck, '-> alto', ek, '|', len(bars), 'bars')

if __name__ == '__main__':
    main(*sys.argv[1:5])
