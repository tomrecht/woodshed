"""Convert an OpenBook .ly.tera tune (default version's Voice + Chords parts) to an ABC body (L:1/8) with chord symbols.

Usage: python3 ly2abc.py file.ly.tera  -> prints JSON {abc, key, title, warnings}
Pitches are concert (LilyPond absolute mode: c = C3, c' = C4)."""
import re, sys, json
from fractions import Fraction as F

NOTE = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
LETTERS = 'cdefgab'


def parse_pitch(name):
    """'fis' -> ('f', 1); 'bes' -> ('b', -1); 'ees'/'es' -> ('e', -1); 'aes'/'as' -> ('a', -1)."""
    l = name[0]; rest = name[1:]; alt = 0
    if l in 'ea' and rest.startswith('s') and not rest.startswith('is'):
        alt -= 1; rest = rest[1:]
    while rest:
        if rest.startswith('is'): alt += 1; rest = rest[2:]
        elif rest.startswith('es'): alt -= 1; rest = rest[2:]
        else: raise ValueError(name)
    return l, alt


def tokenize(s):
    s = re.sub(r'%\{.*?%\}', ' ', s, flags=re.S)
    s = re.sub(r'%[^\n]*', ' ', s)
    toks = re.findall(r'"(?:[^"\\]|\\.)*"|\\[A-Za-z]+|<<|>>|[{}<>~|]|[A-Za-z]+[\',]*!?\??(?:\d+\.*)?(?:\*\d+(?:/\d+)?)?(?::[\w.+\-^]*)?(?:/\+?[a-z]+)?|\d+\.*\*\d+(?:/\d+)?|\d+/\d+|\d+\.+|\d+|=|[-_^][.>^_!+\-]|[()\[\]]|#"[^"]*"|#[^\s{}]+|\S', s)
    return toks


def skip_block(toks, i):
    """toks[i] == '{' -> index after matching '}'"""
    depth = 0
    while i < len(toks):
        if toks[i] == '{': depth += 1
        elif toks[i] == '}':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return i


DUR_RE = re.compile(r'^(\d+)(\.*)(?:\*(\d+)(?:/(\d+))?)?')


def dur_of(spec, prev):
    if not spec: return prev
    m = DUR_RE.match(spec)
    base = F(1, int(m.group(1)))
    d = base; add = base
    for _ in m.group(2): add /= 2; d += add
    if m.group(3): d *= int(m.group(3))
    if m.group(4): d /= int(m.group(4))
    return d


class Parser:
    """Walks a LilyPond music expression in written order (repeats not unfolded), producing events."""

    def __init__(self, chords=False):
        self.chords = chords; self.ev = []; self.t = F(0); self.prev = F(1, 4); self.marks = []
        self.tup = None; self.tupid = 0; self.meta = []; self.warn = []
        self.ref = None if chords else (0, 4)   # relative mode: reference (letter index, octave); start at c' = C4
        self.absdepth = None

    def run(self, toks):
        self.toks = toks; self.i = 0; self.music()

    def music(self, stop=None):
        T = self.toks
        while self.i < len(T):
            tk = T[self.i]
            if tk == '}': self.i += 1; return
            if tk == '{': self.i += 1; self.music(); continue
            if tk in ('<<', '>>'): self.i += 1; continue
            if tk == '\\repeat':
                kind = T[self.i + 1]; n = T[self.i + 2]; self.i += 3
                if kind == 'volta':
                    self.marks.append((self.t, '|:'))
                    assert T[self.i] == '{', T[self.i:self.i + 3]; self.i += 1; self.music()
                    if self.i < len(T) and T[self.i] == '\\alternative':
                        self.i += 1; assert T[self.i] == '{'; self.i += 1; k = 0
                        while T[self.i] != '}':
                            if T[self.i] == '{':
                                k += 1; self.marks.append((self.t, ':|[%d' % k if k > 1 else '[1'))
                                self.i += 1; self.music()
                            else: self.i += 1
                        self.i += 1
                        self.marks.append((self.t, '||'))
                    else:
                        self.marks.append((self.t, ':|'))
                else:   # unfold / percent: play body n times
                    start = self.i
                    for r in range(int(n)):
                        self.i = start; assert T[self.i] == '{'; self.i += 1; self.music()
                continue
            if tk in ('\\tuplet', '\\times'):
                frac = T[self.i + 1]; self.i += 2
                p, q = map(int, frac.split('/'))
                if tk == '\\times': p, q = q, p     # \times 2/3 == \tuplet 3/2
                if re.fullmatch(r'\d+', T[self.i]): self.i += 1   # span duration
                self.tupid += 1; old = self.tup; self.tup = (F(q, p), self.tupid, p, q)
                assert T[self.i] == '{'; self.i += 1; self.music(); self.tup = old
                continue
            if tk == '\\partial':
                self.partial = dur_of(T[self.i + 1], None); self.i += 2; continue
            if tk == '\\time':
                self.meta.append((self.t, 'M', T[self.i + 1])); self.i += 2; continue
            if tk == '\\key':
                l, a = parse_pitch(T[self.i + 1]); mode = T[self.i + 2]
                self.meta.append((self.t, 'K', (l, a, mode))); self.i += 3; continue
            if tk == '\\tempo':
                self.i += 1
                if T[self.i].startswith('"'): self.i += 1
                if self.i + 2 < len(T) and re.fullmatch(r'\d+\.*', T[self.i]) and T[self.i + 1] == '=': self.i += 3
                continue
            if tk in ('\\markup', '\\mark'):
                self.i += 1
                while self.i < len(T) and T[self.i].startswith('\\') and T[self.i] not in ('\\markup',): self.i += 1
                if self.i < len(T) and T[self.i] == '\\markup': self.i += 1
                while self.i < len(T) and T[self.i].startswith('\\'): self.i += 1
                if self.i < len(T) and T[self.i] == '{': self.i = skip_block(T, self.i)
                elif self.i < len(T) and (T[self.i].startswith('"') or T[self.i].startswith('#')): self.i += 1
                continue
            if tk == '\\myMark':
                self.i += 2; continue
            if tk in ('\\once',): self.i += 1; continue
            if tk in ('\\omit', '\\override', '\\set'): self.i += 2; continue
            if tk == '\\fermata':
                if self.ev: self.ev[-1]['ferm'] = True
                self.i += 1; continue
            if tk == '\\absolute':
                # \absolute { ... }: absolute octaves inside
                self.i += 1; saved = self.ref; self.ref = None
                if T[self.i] == '{': self.i += 1; self.music()
                self.ref = saved; continue
            if tk == '\\relative':
                self.i += 1
                if re.match(r"^[a-g]", T[self.i]):
                    m2 = re.match(r"^([a-z]+)([',]*)", T[self.i]); l2, _ = parse_pitch(m2.group(1))
                    self.ref = (LETTERS.index(l2), 3 + m2.group(2).count("'") - m2.group(2).count(','))
                    self.i += 1
                continue
            if tk == '\\chordmode' or tk.startswith('\\'):
                self.i += 1; continue
            if tk == '~':
                if self.ev: self.ev[-1]['tie'] = True
                self.i += 1; continue
            if tk == '<' and not self.chords:   # chord of notes in the melody: keep the top note
                j = self.toks.index('>', self.i); inner = T[self.i + 1:j]; self.i = j + 1
                spec = ''
                if self.i < len(T) and re.fullmatch(r'\d+\.*(?:\*\d+(?:/\d+)?)?', T[self.i]): spec = T[self.i]; self.i += 1
                saved = None; pitches = []
                for x in inner:
                    if re.match(r'[a-g]', x):
                        pitches.append(self.note_pitch(x))
                        if saved is None: saved = self.ref
                if saved is not None: self.ref = saved   # after a chord, relative mode refers to its first note
                self.add('n', pitches[-1:] if pitches else [], spec)
                continue
            m = re.match(r"^([a-gRrs][a-z]*)([',]*)([!?]?)(\d+\.*(?:\*\d+(?:/\d+)?)?)?(?::([\w.+\-^]*))?(?:/\+?([a-z]+))?$", tk)
            if m:
                name, octs, _, spec, qual, bass = m.groups()
                if name in ('R', 'r', 's'): self.add('r', [], spec or '', sym='' if name == 's' and self.chords else None)
                elif self.chords:
                    if name == 'q': name = self.lastroot
                    self.lastroot = name
                    self.add('c', [], spec or '', sym=chord_sym(name, qual, bass))
                else:
                    if name == 'q': self.add('n', self.ev[-1]['p'] if self.ev else [], spec or ''); self.i += 1; continue
                    self.add('n', [self.note_pitch(name + octs)], spec or '')
                self.i += 1; continue
            self.i += 1   # articulations, slurs, bar checks, etc.

    def note_pitch(self, tok):
        m = re.match(r"^([a-z]+)([',]*)", tok); l, a = parse_pitch(m.group(1))
        shift = m.group(2).count("'") - m.group(2).count(',')
        if self.ref is None:
            o = 3 + shift
        else:
            ri, ro = self.ref; li = LETTERS.index(l)
            # nearest octave: steps within a fourth of the previous note
            best = None
            for oo in (ro - 1, ro, ro + 1):
                dist = (oo * 7 + li) - (ro * 7 + ri)
                if -3 <= dist <= 3: best = oo; break
            o = best + shift
            self.ref = (li, o)
        return (l, a, o)

    def add(self, kind, pitches, spec, sym=None):
        d = dur_of(spec, self.prev) if spec else self.prev
        if spec: self.prev = dur_of(spec, self.prev)
        actual = d * self.tup[0] if self.tup else d
        e = {'k': kind, 'p': pitches, 'd': actual, 'nom': d, 't': self.t, 'tup': self.tup, 'tie': False, 'ferm': False}
        if sym is not None: e['sym'] = sym
        self.ev.append(e); self.t += actual


EXT = {'9-': 'b9', '9+': '#9', '5-': 'b5', '5+': '#5', '11+': '#11', '13-': 'b13'}


def chord_sym(root, qual, bass):
    l, a = parse_pitch(root)
    name = l.upper() + ('#' * a if a > 0 else 'b' * -a)
    q = qual or ''
    parts = [p for p in q.split('.') if p != '']
    base = parts[0] if parts else ''
    ext = parts[1:]
    out = {'': '', 'm': 'm', 'maj': '', 'maj7': 'maj7', 'm7': 'm7', '7': '7', '6': '6', 'm6': 'm6', '9': '9', 'm9': 'm9',
           '11': '11', 'm11': 'm11', '13': '13', 'm13': 'm13', 'maj9': 'maj9', 'maj13': 'maj13', 'dim': '°', 'dim7': '°7',
           'aug': '+', 'aug7': '+7', 'sus4': 'sus', 'sus2': 'sus2', 'sus': 'sus', 'm7+': 'm(maj7)', 'mmaj7': 'm(maj7)',
           '7+': '+7', 'h': 'ø7', 'h7': 'ø7', '6.9': '69', '1.5': '5', '5': '5', '2': '2', 'add9': 'add9'}.get(base)
    if out is None: out = base
    extra = ''
    for e in ext:
        if e in EXT: extra += EXT[e]
        elif e == '9' and out in ('6',): out = '69'
        elif e == '9' and out == '7': out = '9'
        elif e == '9' and out == 'm7': out = 'm9'
        elif e == '9' and out == 'm6': out = 'm69'
        elif e == '11' and out in ('7', '9'): out = '11'
        elif e == '13' and out in ('7', '9'): out = '13'
        elif e == '7' and out == 'm': out = 'm7'
        elif e == '7' and out == 'sus': out = '7sus'
        elif e == '7' and out == '': out = '7'
        elif e in ('9', '11', '13', '7'): extra += e
        elif e == '6': out = out + '6' if out in ('m',) else '6'
        else: extra += e
    if out == 'm7' and extra == 'b5': out, extra = 'ø7', ''
    if out == '°' and extra == '7': out, extra = '°7', ''
    if out == '7' and extra == '#5': out, extra = '+7', ''
    q2 = out + extra
    q2 = {'9-': '7b9', '9+': '7#9', 'maj79': 'maj9', '75': '7', '7sus4': '7sus', '9sus4': '9sus', '711+^95': '7#11', '7b5b9': '7b9b5'}.get(q2, q2)
    q2 = re.sub(r'\^\d+', '', q2)
    s = name + q2
    if bass:
        bl, ba = parse_pitch(bass); s += '/' + bl.upper() + ('#' * ba if ba > 0 else 'b' * -ba)
    return s


def part(src, kind, ver):
    m = re.search(r'part == "%s%s" %%\}(.*?)\{%% endif' % (kind, ver), src, re.S)
    return m.group(1) if m else None


# ---------- ABC output ----------
KEYS_MAJ = {('c', 0): 0, ('g', 0): 1, ('d', 0): 2, ('a', 0): 3, ('e', 0): 4, ('b', 0): 5, ('f', 1): 6, ('c', 1): 7,
            ('f', 0): -1, ('b', -1): -2, ('e', -1): -3, ('a', -1): -4, ('d', -1): -5, ('g', -1): -6, ('c', -1): -7}
REL = {'minor': 3}   # minor key = major key a minor third up
SHARPS = 'fcgdaeb'; FLATS = 'beadgcf'


def key_info(l, a, mode):
    pc = (NOTE[l] + a) % 12
    if mode == 'minor':
        # relative major: up a minor third, letter up 2
        ml = LETTERS[(LETTERS.index(l) + 2) % 7]; mpc = (pc + 3) % 12; ma = (mpc - NOTE[ml] + 6) % 12 - 6
        nacc = KEYS_MAJ[(ml, ma)]
    else:
        nacc = KEYS_MAJ[(l, a)]
    sig = {x: 0 for x in LETTERS}
    if nacc > 0:
        for x in SHARPS[:nacc]: sig[x] = 1
    else:
        for x in FLATS[:-nacc]: sig[x] = -1
    name = l.upper() + ('#' if a > 0 else 'b' if a < 0 else '') + ('m' if mode == 'minor' else '')
    return name, sig


def pitch_abc(p, acc):
    l, a, o = p
    s = {1: '^', 2: '^^', -1: '_', -2: '__', 0: '='}[a] if acc else ''
    if o >= 5: s += l + "'" * (o - 5)
    else: s += l.upper() + ',' * (4 - o)
    return s


def len_abc(d):   # d in whole notes -> L:1/8 units
    u = d * 8
    if u == 1: return ''
    if u.denominator == 1: return str(u.numerator)
    if u.numerator == 1: return '/' * 0 + '/' + str(u.denominator) if u.denominator != 2 else '/'
    return '%d/%d' % (u.numerator, u.denominator)


def convert(path):
    src = open(path).read()
    ver = re.search(r'default_version = "(\w+)"', src).group(1)
    title = re.search(r'^title = "(.*)"', src, re.M).group(1)
    v, c = part(src, 'Voice', ver), part(src, 'Chords', ver)
    P = Parser(); P.run(tokenize(v))
    C = Parser(chords=True); C.run(tokenize(c)) if c else None
    warn = []
    # meter / key timeline
    meters = [(t, x) for t, k, x in P.meta if k == 'M'] or [(F(0), '4/4')]
    keys = [(t, x) for t, k, x in P.meta if k == 'K'] or [(F(0), ('c', 0, 'major'))]
    partial = getattr(P, 'partial', F(0))
    # bar boundaries in written time
    end = P.t; bars = []; t = F(0)
    if partial: bars.append(partial); t = partial
    mi = 0
    while t < end:
        while mi + 1 < len(meters) and meters[mi + 1][0] <= t: mi += 1
        num, den = map(int, meters[mi][1].split('/')); t += F(num, den); bars.append(t)
    barset = set(bars)
    # chord symbols by start time
    syms = {}
    if c:
        for e in C.ev:
            if e.get('sym') and e['k'] == 'c': syms.setdefault(e['t'], e['sym'])
    if abs(C.t - P.t) > F(1, 4) if c else False: warn.append('chord length %s vs melody %s' % (C.t, P.t))
    # split events at bar lines and chord times (not inside tuplets)
    cuts = sorted(barset | set(syms))
    evs = []
    for e in P.ev:
        if e['tup']:
            evs.append(e); continue
        s, f = e['t'], e['t'] + e['d']
        pts = [x for x in cuts if s < x < f]
        if not pts: evs.append(e); continue
        segs = [s] + pts + [f]
        for i in range(len(segs) - 1):
            ne = dict(e); ne['t'] = segs[i]; ne['d'] = ne['nom'] = segs[i + 1] - segs[i]
            ne['tie'] = e['tie'] if i == len(segs) - 2 else (e['k'] == 'n')
            ne['ferm'] = e['ferm'] if i == len(segs) - 2 else False
            evs.append(ne)
    # render
    kname, sig = key_info(*keys[0][1])
    first_meter = meters[0][1]
    out = []; line = []; bar_state = {}; nbar = 0
    marks = {}
    for t, mk in P.marks: marks.setdefault(t, []).append(mk)
    ki = 0; mi = 0; used_syms = set()
    def flush_bar(t, closing):
        nonlocal nbar
        mk = marks.pop(t, [])
        bl = '|'
        if any(x.startswith(':|') for x in mk) or ':|' in mk: bl = ':|'
        if '||' in mk and bl == '|': bl = '||'
        if closing: bl = '|]' if bl == '|' else bl
        start = ''
        if '|:' in mk: start = '|:' if bl == '|' else ''
        alt = [x for x in mk if '[' in x]
        txt = bl
        if '|:' in mk:
            txt = {'|': '|:', ':|': ':||:', '||': '||:'}.get(bl, bl + '|:') if not closing else bl
        if alt: txt += ' [' + alt[0].split('[')[1]
        line.append(' ' + txt + ' ')
        nbar += 1
        if nbar % 4 == 0: line.append('\n')
    # opening marks at t=0
    if '|:' in marks.get(F(0), []): line.append('|: '); marks[F(0)].remove('|:')
    tupopen = None
    for idx, e in enumerate(evs):
        t = e['t']
        if t in barset and t != 0 and t != evs[0]['t']:
            pass
        while ki + 1 < len(keys) and keys[ki + 1][0] <= t:
            ki += 1; kname2, sig = key_info(*keys[ki][1]); line.append('[K:%s] ' % kname2)
        while mi + 1 < len(meters) and meters[mi + 1][0] <= t:
            mi += 1; line.append('[M:%s] ' % meters[mi][1])
        tok = ''
        if e['tup'] and (tupopen != e['tup'][1]):
            ratio, tid, p, q = e['tup']; n = sum(1 for x in evs if x['tup'] and x['tup'][1] == tid)
            tok += '(%d:%d:%d' % (p, q, n); tupopen = tid
        if not e['tup']: tupopen = None
        sym = syms.get(t)
        if sym is None and e['tup'] is None:
            pass
        if sym is not None and t not in used_syms:
            tok = '"%s"' % sym + tok; used_syms.add(t)
        elif e['tup']:
            # chord inside a tuplet that does not start on a note: attach to this note if it begins within it
            for st in list(syms):
                if st not in used_syms and t <= st < t + e['d']: tok = '"%s"' % syms[st] + tok; used_syms.add(st)
        if e['ferm']: tok += '!fermata!'
        L = len_abc(e['nom'])
        if e['k'] == 'r' or not e['p']:
            tok += 'z' + L
        else:
            p = e['p'][0]; l, a, o = p
            cur = bar_state.get((l, o), sig[l])
            acc = cur != a
            bar_state[(l, o)] = a
            tok += pitch_abc(p, acc) + L + ('-' if e['tie'] else '')
        line.append(tok + ' ')
        tend = t + e['d']
        if tend in barset:
            bar_state = {}
            flush_bar(tend, tend == evs[-1]['t'] + evs[-1]['d'])
        elif tend in marks:
            mk = marks.pop(tend)
            if '|:' in mk: line.append(' |: ')
            alt = [x for x in mk if '[' in x]
            if any(x.startswith(':|') for x in mk): line.append(' :| ')
            if alt: line.append(' [' + alt[0].split('[')[1] + ' ')
    abc = ''.join(line)
    abc = re.sub(r' +', ' ', abc).replace(' \n', '\n').replace('\n ', '\n').strip()
    if not abc.rstrip().endswith(('|]', ':|', '||')): abc += ' |]'
    if first_meter != '4/4': abc = 'M:%s\n' % first_meter + abc
    if len(used_syms) < len(syms): warn.append('%d chords not placed' % (len(syms) - len(used_syms)))
    return {'title': title, 'key': kname, 'abc': abc, 'warn': warn}


if __name__ == '__main__':
    print(json.dumps(convert(sys.argv[1]), indent=1, ensure_ascii=False))
