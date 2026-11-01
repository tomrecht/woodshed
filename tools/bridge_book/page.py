import json, html
EX=json.load(open('ex.json'))
secs=[]; 
for s,*_ in EX:
    if s not in secs: secs.append(s)
toc=''; body=''; n=0; cur=None
for i,(s,t,txt,abc) in enumerate(EX):
    if s!=cur:
        first=n+1; cnt=sum(1 for x in EX if x[0]==s)
        toc+=f'<tr><td>{html.escape(s)}</td><td>Nos. {first}–{first+cnt-1}</td></tr>'
        body+=f'<h2 class="sec">{html.escape(s)}</h2>'; cur=s
    n+=1
    body+=f'<div class="ex"><h3><span>{n}.</span> {html.escape(t)}</h3><p>{html.escape(txt)}</p><div class="abc" id="a{n}"></div></div>'
abcs=json.dumps([e[3] for e in EX])
open('book.html','w').write(f'''<!doctype html><html><head><meta charset="utf-8"><title>Crossing the Bridge</title>
<style>
@page {{ size: A4; margin: 16mm 15mm 18mm; }}
body {{ font-family: Georgia, 'DejaVu Serif', serif; color:#1d1d1d; margin:0; }}
.cover {{ height: 255mm; display:flex; flex-direction:column; justify-content:center; text-align:center; page-break-after:always; }}
.cover h1 {{ font-size: 46pt; margin:0; letter-spacing:1px; }}
.cover .sub {{ font-size: 17pt; font-style:italic; margin-top:10px; color:#444; }}
.cover .rule {{ width:60%; margin:28px auto; border-top:2px solid #333; }}
.cover .meta {{ font-size: 12pt; color:#555; }}
.intro {{ page-break-after: always; font-size: 10.5pt; line-height:1.45; }}
.intro h2 {{ font-size: 17pt; border-bottom:1px solid #999; padding-bottom:3px; }}
.intro li {{ margin-bottom: 5px; }}
table {{ border-collapse:collapse; width:100%; margin-top:6px; }}
td {{ padding:3px 6px; border-bottom:1px dotted #bbb; }}
h2.sec {{ font-size: 16pt; margin: 6mm 0 2mm; border-bottom:2px solid #333; padding-bottom:2px; page-break-after: avoid; }}
h2.sec:not(:first-of-type) {{ page-break-before: always; }}
.ex {{ page-break-inside: avoid; margin-bottom: 5mm; }}
.ex h3 {{ font-size: 12pt; margin: 0 0 1mm; }}
.ex h3 span {{ color:#8a3b12; }}
.ex p {{ font-size: 9.5pt; margin: 0 0 1mm; color:#333; font-style: italic; line-height:1.35; }}
.abc svg {{ display:block; }}
</style></head><body>
<div class="cover"><h1>Crossing the Bridge</h1><div class="sub">{len(EX)} Exercises for Clarinet over the Break</div><div class="rule"></div>
<div class="meta">Chromatic · Seconds · Thirds · Intervals · Arpeggios · Patterns · Études<br><br>All music at written pitch (B♭ or A clarinet)</div></div>
<div class="intro"><h2>About this book</h2>
<p>The “break” or “bridge” is the move between the throat register (written G4–B♭4, the notes around and above the middle line of the treble staff) and the clarion register, starting at written B4 on the middle line. Going from a throat tone with almost no fingers down to a clarion note with nearly every hole covered and the register key open asks the whole hand to move at once. These exercises concentrate on exactly that crossing, in every common key and pattern.</p>
<h2>How to practise</h2><ul>
<li><b>Slow first.</b> Start each exercise at ♩ = 60 or slower. Raise the metronome only when the crossing is clean and even three times running.</li>
<li><b>Right hand down.</b> On the throat tones (G, G♯, A, B♭), keep the right-hand fingers down. Most notes keep their pitch, often sound better, and the clarion note then needs only the left hand and thumb.</li>
<li><b>Roll the thumb.</b> Keep the left thumb touching the register key and tilt it open; don’t lift it away and come back.</li>
<li><b>Fingers together.</b> Uneven fingers cause the squeak or “blip” in the middle of a crossing. Move all fingers as one gesture, close to the keys.</li>
<li><b>Air leads, not lips.</b> Keep the air fast and the voicing high and steady across the break; don’t bite on the clarion notes.</li>
<li><b>Articulation variants.</b> Play each exercise slurred (as marked), then fully tongued, then slur-two / tongue-two, then tongue-one / slur-three.</li>
<li><b>Rhythm variants.</b> For running eighths, also try dotted rhythms (long–short and short–long) to drill the crossing at both speeds.</li>
<li><b>Transpose.</b> The scale and pattern exercises can be played in any key; once comfortable, work through all twelve.</li>
</ul>
<h2>Contents</h2><table>{toc}</table></div>
{body}
<script src="../../vendor/abcjs-basic-min.js"></script>
<script>
const A={abcs};
A.forEach((a,i)=>ABCJS.renderAbc('a'+(i+1),a,{{staffwidth:700,paddingtop:0,paddingbottom:0,paddingleft:0,paddingright:0,responsive:'resize',scale:1.0}}));
document.body.dataset.done='1';
</script></body></html>''')
