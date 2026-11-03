"""Build a Woodshed sheet-music pack (melodies only) from OpenBook (github.com/veltzer/openbook, MIT).

Usage: git clone --depth 1 https://github.com/veltzer/openbook.git /tmp/openbook
       python3 make_pack.py /tmp/openbook out.json "Tune Up=tune_up" "Milestones (New)=milestones" ...
Each argument is "<iReal title>=<openbook file stem>". The pack is concert pitch (pitch 'C');
import it in the app with Progress > Import sheet music. Melodies are copyrighted: keep packs out of this repo."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ly2abc import convert

src, out, *pairs = sys.argv[1:]
tunes = []
for p in pairs:
    name, stem = p.split('=', 1)
    r = convert(os.path.join(src, 'src', 'openbook', stem + '.ly.tera'))
    if r['warn']: print('WARN', name, r['warn'])
    tunes.append({'name': name, 'lead': {'abc': r['abc'], 'key': r['key']}, 'pages': []})
json.dump({'app': 'woodshed-sheets', 'v': 1, 'pitch': 'C', 'title': 'OpenBook melodies', 'tunes': tunes}, open(out, 'w'), ensure_ascii=False)
print(len(tunes), 'tunes ->', out)
