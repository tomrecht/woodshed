import json, html
SH="FCGDAEB"; FL="BEADGCF"; L="CDEFGAB"
KEYS={'C':0,'G':1,'D':2,'A':3,'E':4,'F':-1,'Bb':-2,'Eb':-3,'Ab':-4,
      'Am':0,'Em':1,'Bm':2,'Dm':-1,'Gm':-2,'Cm':-3}
def keyalt(k):
    n=KEYS[k]; a={c:0 for c in L}
    for c in (SH[:n] if n>0 else FL[:-n]): a[c]=1 if n>0 else -1
    return a
def D(name):  # 'C4' -> diatonic index
    return int(name[1:])*7+L.index(name[0])
def nm(d):
    l=L[d%7]; o=d//7
    if o>=5: return l.lower()+"'"*(o-5)
    return l+","*(4-o)
SP={0:(0,0),1:(0,1),2:(1,0),3:(1,1),4:(2,0),5:(3,0),6:(3,1),7:(4,0),8:(4,1),9:(5,0),10:(5,1),11:(6,0)}
FP={1:(1,-1),3:(2,-1),6:(4,-1),8:(5,-1),10:(6,-1)}
def chrom(m,flat=False):
    pc=m%12; li,al=(FP[pc] if flat and pc in FP else SP[pc]); return ((m//12-1)*7+li,al)
def M(n): # 'G4' -> midi
    return {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[n[0]]+12*(int(n[-1])+1)+(1 if '#' in n else -1 if 'b' in n else 0)
def dec(r):
    out=[]
    for v in (12,8,6,4,3,2,1):
        while r>=v: out.append(v); r-=v
    return out
def build(notes,key='C',meter='4/4',barlen=8,beam=4,bpl=4,slur=True,final=None):
    """notes: list of (d,alt) eighths; final: (d,alt) held to end"""
    ka=keyalt(key); bars=[]; cur=[]
    for n in notes:
        cur.append((n,1,False))
        if len(cur)==barlen: bars.append(cur); cur=[]
    if final is not None:
        rem=barlen-len(cur) if cur else barlen
        parts=dec(rem)
        cur=cur+[(final,p,i<len(parts)-1) for i,p in enumerate(parts)]; bars.append(cur); cur=[]
    out=[]
    for b in bars:
        st={}; s=''; acc=0
        for (d,al),du,tie in b:
            cur_al=st.get(d,ka[L[d%7]]); pre=''
            if al!=cur_al: pre='^'*al if al>0 else ('_'*-al if al<0 else '='); st[d]=al
            s+=pre+nm(d)+(str(du) if du!=1 else '')+('-' if tie else ''); acc+=du
            if acc%beam==0: s+=' '
        s=s.strip()
        if slur and len(b)>2 and all(du==1 for _,du,_t in b): s='('+s+')'
        out.append(s)
    lines=[]
    for i in range(0,len(out),bpl):
        lines.append(' | '.join(out[i:i+bpl]))
    body=' |\n'.join(lines)+' |]'
    return f"X:1\nM:{meter}\nL:1/8\nK:{key}\n{body}\n"
def parts_of(b,final):
    # trailing held entries of the final note (the decomposition)
    k=0
    for (n,du) in reversed(b):
        if n==final and (du>1 or k==0): k+=1
        else: break
    # first note of decomposition may be a 1-eighth which equals an earlier stream note; ok
    return [0]*k
def dia(key,seq):
    ka=keyalt(key); return [(d,ka[L[d%7]]) for d in seq]
def updown(pat,lo,hi,step=1):
    """pat: offsets; ascend from lo while top<=hi, then descend mirrored"""
    top=max(pat); up=[]; i=lo
    while i+top<=hi:
        up+= [i+o for o in pat]; i+=step
    dn=[]; i=hi
    while i-top>=lo:
        dn+= [i-o for o in pat]; i-=step
    return up+dn
def lo_of(key,span=11):
    t=key.rstrip('m')[0]; d=D(t+'4')
    return d if d+span<=D('B5') or d-7<D('E3') else d-7

EX=[]  # (section, title, text, abc)
def add(sec,title,text,abc): EX.append((sec,title,text,abc))

S1="I. Foundations"
add(S1,"Long-tone slurs across the break",
 "Half notes, ♩ = 60. Slur each pair without a gap. Keep the air fast and the voicing (tongue position) high on the throat note so the clarion note pops out without a bump. Right-hand fingers stay down on the throat tones.",
 "X:1\nM:4/4\nL:1/8\nK:C\n(A4 B4) | (B4 A4) | (_B4 =B4) | (B4 _B4) | (A4 c4) | (c4 A4) | (G4 B4) | (B4 G4) |\n(^G4 B4) | (B4 ^G4) | (_B4 c4) | (c4 _B4) | (A4 d4) | (d4 A4) | (G4 c4) | c8 |]\n")
add(S1,"Right hand down: throat tones",
 "Play the throat tones with all three right-hand fingers (and the little finger on the low B/C key if comfortable) held down. Pitch and tone usually improve, and the clarion note is then only a left-hand move away. Compare one bar 'hands off', one bar 'right hand down'.",
 "X:1\nM:4/4\nL:1/8\nK:C\nG4 A4 | _B4 A4 | G2 A2 _B2 A2 | G8 |\n(A2 B2 A2 B2) | (_B2 =B2 _B2 =B2) | (A2 c2 A2 c2) | B8 |]\n")
add(S1,"Twelfths: chalumeau to clarion",
 "Finger the low note, add the register key, and the instrument jumps a twelfth into the clarion. Slur each pair; the low note should not change shape or embouchure when the thumb opens the register key. This trains the air support every bridge crossing needs.",
 "X:1\nM:4/4\nL:1/8\nK:C\n(E,4 B4) | (F,4 c4) | (^F,4 ^c4) | (G,4 d4) |\n(^G,4 ^d4) | (A,4 e4) | (_B,4 f4) | (B,4 ^f4) |\n(C4 g4) | (^C4 ^g4) | (D4 a4) | C8 |]\n")
add(S1,"Leaps from the throat into the clarion",
 "Quarter notes, slurred. Each leap starts on a throat tone and lands on a clarion note. Aim for the top note with air, not jaw pressure.",
 "X:1\nM:4/4\nL:1/8\nK:C\n(G2 d2 G2 e2) | (A2 d2 A2 e2) | (_B2 =d2 _B2 f2) | (A2 c2 A2 B2) |\n(G2 c2 A2 d2) | (_B2 =c2 A2 B2) | (G2 e2 A2 f2) | g8 |]\n")
add(S1,"Bridge tremolos I",
 "Sixteenth notes, start ♩ = 50. Alternate across the break as evenly as possible. Move all fingers together; listen for any 'blip' between the notes.",
 "X:1\nM:4/4\nL:1/16\nK:C\n(ABAB ABAB ABAB ABAB) | (A8 B8) | (^GBGB GBGB GBGB GBGB) | (^G8 B8) |\n(_Bc_Bc _Bc_Bc _Bc_Bc _Bc_Bc) | (_B8 c8) | (AcAc AcAc AcAc AcAc) | (A8 c8) |]\n")
add(S1,"Bridge tremolos II",
 "Wider tremolos. The throat note's right hand stays down throughout, so only the left hand and thumb move.",
 "X:1\nM:4/4\nL:1/16\nK:C\n(GcGc GcGc GcGc GcGc) | (G8 c8) | (AdAd AdAd AdAd AdAd) | (A8 d8) |\n(_Bd_Bd _Bd_Bd _Bd_Bd _Bd_Bd) | (_B8 =d8) | (GdGd GdGd GdGd GdGd) | (G8 d8) |]\n")

S2="II. Chromatic"
def ch(lo,hi,group=None):
    a=list(range(M(lo),M(hi)+1)); return [chrom(m) for m in a]+[chrom(m,True) for m in reversed(a[:-1])][:-0 or None]
seq=[chrom(m) for m in range(M('G4'),M('D5')+1)]+[chrom(m,True) for m in range(M('C#5'),M('G4')-1,-1)]
seq=seq*1
add(S2,"Chromatic: G4 to D5","Eighth notes, slurred, ♩ = 60 → 120. The core of the bridge. Use the right-hand side key for B♭/A♯ only if your teacher prefers; otherwise use the standard throat fingering with the right hand down.",
 build(seq[:-1]+seq[:-1],final=chrom(M('G4'))))
seq=[chrom(m) for m in range(M('E4'),M('G5')+1)]+[chrom(m,True) for m in range(M('F#5'),M('E4')-1,-1)]
add(S2,"Chromatic: E4 to G5","A wider chromatic sweep. Keep the tone the same colour from the bottom to the top; the break should be invisible.",
 build(seq[:-1],final=chrom(M('E4'))))
seq=[]
for s in range(M('F4'),M('C5')+1): seq+= [chrom(s+i) for i in range(4)]
for s in range(M('D5'),M('A4')-1,-1): seq+= [chrom(s-i,True) for i in range(4)]
add(S2,"Chromatic groups of four","Each group of four starts a half step higher, then a half step lower on the way down. Slur in groups of four, then all tongued.",
 build(seq,final=chrom(M('F4'))))
seq=[]
for s in range(M('G4'),M('D5')+1): seq+=[chrom(s),chrom(s+1),chrom(s),chrom(s-1)]
add(S2,"Chromatic neighbour notes","Upper and lower chromatic neighbours around every note of the bridge. Many of these cross the break twice per beat.",
 build(seq,final=chrom(M('D5'))))
seq=[chrom(m) for m in range(M('F#4'),M('F5')+1)]+[chrom(m,True) for m in range(M('E5'),M('F#4')-1,-1)]
add(S2,"Chromatic triplets","Compound meter, three notes per beat. Accent the first of each group lightly so the groupings fall in different places on the instrument.",
 build(seq[:-1],meter='12/8',barlen=12,beam=3,bpl=3,final=chrom(M('F#4'))))
seq=[]
for s in range(M('E4'),M('B4')+1): seq+=[chrom(s),chrom(s+3),chrom(s+1),chrom(s+4)]
for s in range(M('D5'),M('G4')-1,-1): seq+=[chrom(s,True),chrom(s-3,True),chrom(s-1,True),chrom(s-4,True)]
add(S2,"Chromatic minor thirds","Pairs of minor thirds rising by half steps. A demanding finger-coordination drill: go slowly.",
 build(seq,final=chrom(M('E4'))))

S3="III. Scales in seconds"
for k in ['C','G','F','D','Bb','A','Eb','E']:
    lo=lo_of(k,11); hi=lo+11
    seq=list(range(lo,hi+1))+list(range(hi-1,lo-1,-1))
    seq=seq+seq[1:]
    add(S3,f"{k.replace('b','♭')} major scale over the break",
        "Two times through, slurred; then tongued. Hold the top and bottom notes steady in pitch. ♩ = 60 → 132.",
        build(dia(k,seq[:-1]),key=k,final=dia(k,[lo])[0]))
S4="IV. Thirds"
for k in ['C','G','F','D','Bb','A']:
    lo=lo_of(k,9); hi=lo+9
    seq=updown([0,2],lo,hi)
    add(S4,f"Thirds in {k.replace('b','♭')} major","Broken thirds up and down. Many pairs straddle the break: make each pair a single gesture.",
        build(dia(k,seq),key=k,final=dia(k,[lo])[0]))
S5="V. Harmonic minor"
for k in ['Am','Em','Dm','Gm']:
    lo=lo_of(k,9); hi=lo+9; ka=keyalt(k); t=L[lo%7]; lead=L[(lo+6)%7]
    seq=list(range(lo,hi+1))+list(range(hi-1,lo-1,-1))
    seq=seq+seq[1:]
    notes=[(d, ka[L[d%7]]+(1 if L[d%7]==lead else 0)) for d in seq[:-1]]
    add(S5,f"{k[0]} harmonic minor","The raised seventh adds an awkward augmented second; several fall right at the break.",
        build(notes,key=k,final=(lo,ka[t])))
S6="VI. Patterns"
def pat(k,p,title,text,span=9,meter='4/4',barlen=8,beam=4,bpl=4,step=1):
    lo=lo_of(k,span); seq=updown(p,lo,lo+span,step)
    add(S6,title,text,build(dia(k,seq),key=k,meter=meter,barlen=barlen,beam=beam,bpl=bpl,final=dia(k,[lo])[0]))
pat('C',[0,1,2,3],"1-2-3-4 in C major","Four-note scale groups, each starting one step higher.")
pat('G',[0,1,2,4],"1-2-3-5 in G major","A classic pattern; the skip at the end of each group often lands across the break.")
pat('F',[0,1,2,0],"1-2-3-1 in F major","Each group returns to its starting note. Watch the B♭–C–A and similar groups.")
pat('D',[0,2,1,3],"1-3-2-4 in D major","Broken thirds inside a four-note group.")
pat('C',[0,2,4],"Triads on every degree in C","Compound meter. Each triad crosses the break at least once in the middle of the range.",meter='12/8',barlen=12,beam=3,bpl=3)
pat('Bb',[0,2,4],"Triads on every degree in B♭","As above, in B♭ — the throat B♭ to clarion C/D is the hard spot.",meter='12/8',barlen=12,beam=3,bpl=3)
pat('G',[0,2,4,6],"Seventh chords in G major","Four-note arpeggios on each degree. Keep fingers close to the keys.")
pat('F',[0,3],"Fourths in F major","Broken fourths. Every pair should sound as smooth as a step.",span=10)
pat('C',[0,4],"Fifths in C major","Broken fifths: a bigger leap means more air, not more lip.",span=11)
pat('D',[0,5],"Sixths in D major","Broken sixths up and down.",span=11)
pat('G',[0,7],"Octaves in G major","Low note in the chalumeau or throat, high note in the clarion. Keep the throat open on the top note.",span=12)
pat('A',[0,1,0,-1],"Turns in A major","Neighbour-note turns around each scale degree. Ideal for evening out G♯–A–B–C♯.",span=9)
pat('Eb',[0,1,2,1],"Rocking pattern in E♭ major","1-2-3-2 groups. Lots of throat-to-clarion back-and-forth.")
pat('E',[0,2,4,2],"Broken triads in E major","1-3-5-3 shapes. E major puts G♯, A and B right at the break.")
S7="VII. Symmetric scales"
seq=[chrom(m) for m in range(M('F4'),M('F5')+1,2)]+[chrom(m,True) for m in range(M('D#5'),M('F4')-1,-2)]
add(S7,"Whole-tone scale","Whole steps from F4 to F5 and back, twice. The A–B and B–C♯ steps are the challenge.",build(seq[:-1]+seq[:-1],final=chrom(M('F4'))))
seq=[]
for s in [M('E4'),M('F4'),M('F#4'),M('G4')]:
    a=[s+3*i for i in range(5)]; seq+=[chrom(m) for m in a]+[chrom(m,True) for m in reversed(a[1:-1])]
add(S7,"Diminished arpeggios","Stacked minor thirds starting on E, F, F♯ and G. Every arpeggio crosses the break.",build(seq,meter='4/4',final=chrom(M('E4'))))

S8="VIII. Études"
add(S8,"Étude 1 — Bridge Waltz","Legato, ♩ = 112. In F major the throat B♭ moves straight to clarion C again and again. Keep the right hand down on every B♭ and A.",
"X:1\nM:3/4\nL:1/8\nK:F\n(c2 A2 B2 | c4) d2 | (e2 d2 c2 | B4 A2) | (G2 A2 B2 | c2 d2 e2 | f4 e2 | d6) |\n(A2 c2 =B2 | c4 A2) | (B2 d2 c2 | A4 F2) | (G2 B2 d2 | c2 A2 B2 | A2 G2 E2 | F6) |]\n")
add(S8,"Étude 2 — Song over the bridge","Singing tone, ♩ = 72. The melody lives right on the break; make every interval sound like it belongs to one voice.",
"X:1\nM:4/4\nL:1/8\nK:G\n(G2 A2 B2 c2 | d4 B4) | (A2 B2 c2 d2 | B4 G4) | (A2 c2 B2 d2 | c2 e2 d2 B2) | (A2 B2 G2 A2 | B8) |\n(d2 c2 B2 A2 | B2 c2 d4) | (e2 d2 c2 B2 | A2 G2 A4) | (B2 A2 B2 c2 | d2 B2 c2 A2) | (B2 A2 F2 A2 | G8) |]\n")
add(S8,"Étude 3 — Running eighths","♩. = 76 → 116. In D major the B–C♯ crossing comes in nearly every bar. Slur two bars, then tongue two bars.",
"X:1\nM:6/8\nL:1/8\nK:D\n(ABc dcB | ABc d3) | (edc Bcd | c3 A3) | (Bcd edc | BAB cBA) | (GAB cBA | B3 A3) |\n(dcB ABc | def edc) | (Bcd cBA | B3 c3) | (dBG ABc | dcB AGF) | (EFG ABc | d6) |]\n")
add(S8,"Étude 4 — Minor lament","♩ = 66, espressivo. D minor brings the throat B♭ against clarion C♯ — a tricky augmented second across the break.",
"X:1\nM:4/4\nL:1/8\nK:Dm\n(A2 B2 ^c2 d2 | e4 d2 ^c2) | (d2 B2 A2 G2 | A6) z2 | (F2 A2 d2 ^c2 | B2 A2 B2 ^c2) | (d2 e2 f2 e2 | d6) z2 |\n(f2 e2 d2 ^c2 | B2 ^c2 d2 B2) | (A2 B2 A2 G2 | F4 E4) | (D2 F2 A2 d2 | ^c2 B2 A2 G2) | (F2 E2 ^C2 E2 | D8) |]\n")
json.dump(EX,open('ex.json','w'))
print(len(EX))
