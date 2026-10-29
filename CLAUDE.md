# Woodshed – sax practice tracker

Personal web app (installable PWA) for tracking saxophone practice. Live at https://tomrecht.github.io/woodshed/ –
GitHub Pages serves the `main` branch as-is, so **a push to `main` is a deploy**. There is no build step.
**Always push finished changes straight to `main` (owner, 2026-10-24)**, even when a session is set up on another branch.

The owner plays alto sax and often asks for changes from their phone. Keep replies short and say plainly what changed.

## Files
- `index.html` – the whole app: CSS, HTML shell and one `<script>` (vanilla JS, no framework, no dependencies).
- `sw.js` – offline cache. **Bump `CACHE` (`woodshed-vN`) on every deploy**, or phones keep the old version.
  New static files must be added to its `FILES` list.
- `library.json` – ~1,355 chord charts (iReal Pro), as **E♭ (alto) parts**: `{t: title, s: style, c: composer, k: key, ts, b: [bar]}`;
  a bar is `{n, c: [chord symbols], sec?, ro?/rc? (repeat open/close), end? (ending no.), rep? (% bar), mk? (Segno/Coda/D.C.)}`.
- `vendor/abcjs-basic-min.js` – abcjs 6.4.4 (MIT, licence beside it), loaded only when a phrase is shown. ii–V–I phrases are
  exercises with notation. `PHRASES` (built-ins) is empty since 2026-10-25 (owner adds their own; rev 10 removed them); the user's carry `ex.abc` + `ex.abcKey`
  (ABC body, L:1/8, 4/4, chords in quotes). Categories by length since rev 11: `phrases-2` / `phrases-4` (`sec.len`);
  a saved phrase goes to the one matching its bar count (major/minor is just the written key). One tempo for all 12 keys (`keys: ['—']`); shown in any key, octave chosen to
  stay in the sax range, played with melody over `playChords`; "All 12 keys" (`S.settings.phAll`, default on) plays it round the
  cycle of fourths from the chosen key, re-rendering the notation a beat before each key (`phrasePlay` `keys`/`onKey`). The phrase editor can record a take from the mic
  (`recordPhrase`: AudioWorklet capture → YIN pitch → grid of 6 units per beat (eighths, swung or straight, or a triplet beat) → ABC in the written key);
  test the analysis with synthetic audio (`detectNotes`/`quantizeNotes`/`notesToAbc`) and Chrome's fake mic
  (`--use-file-for-fake-audio-capture=file.wav`).
- Audio: notes, drums and phrase melody are created ~3 s before they sound (`soon()` queue, cleared by `earStop`), not all up
  front – hundreds of scheduled sources made phones crackle. New playback code should go through `soon()` too.
- `licks/` lick images, `piano/` Salamander piano samples (CC BY 3.0), `drums/` VCSL drum samples (CC0).
- `tools/ireal_decode.py`, `tools/add_chart.py` – decode iReal Pro forum share links and add a chart to `library.json`
  (converts concert → alto). Forum: https://forums.irealpro.com (XenForo; search with `/search/search?keywords=...`).
- PDFs (the owner's iReal export and lick sheets) are git-ignored and not in the repo.

## Data – never lose the owner's data
- All state lives in `localStorage` key `woodshed.v1` (object `S`), optionally synced to a private GitHub gist.
  Lick photos the user adds live in IndexedDB and sync to the gist as a separate file (`woodshed-images.json`).
- `S.lib` = shared library (sections → exercises, licks, tunes); `S.prog[instrumentId]` = per-instrument progress
  (`bpm`, `hist`, `sessions`, `tunes`, `touched`, `badges`, …).
- Each instrument in `S.inst` has a colour scheme `theme` (key of `THEMES`: accent + tinted dark surfaces, applied as CSS
  variables by `applyTheme()` on every render); new instruments get an unused one, picked in Progress → Instruments.
- Consolidation (`P().cons`, see the comment above `CONS_GAP`): when none is open on today's plan and none is due, `consEarly`
  offers the backlog key that falls due soonest; practising a key that is on the plan as a consolidation item counts even if early.
- Floor keys: `floorTopUp` keeps an unplayed floor key on today's plan whenever a completed exercise has one to offer
  (one taken off the plan stays off that day: `S.plan.floorOut`).
- `p.exDone` = exercises completed (every key logged) → +25 XP once (`exDoneCheck`); 0 = complete before the bonus existed (no XP).
- Every day's plan gets one ii–V–I phrase (`pickPhrase`, the one practised longest ago; `S.plan.ph` marks it done for the day).
- `S.sched` = scheduled practice (once, or weekly on chosen days; optional length; kept by a session on ANY instrument (`slotKept`); phone reminders via ntfy.sh, settings per device in `woodshed.ntfy`); `S.ear` = shared ear-training stats;
  `S.quiz[Eb|Bb|C]` = changes-quiz results per pitch.
- **Tempos are stored as quarter-note BPM.** Items/keys can be shown in half notes (`unit: 2`, exercise `unitKeys`).
- Tunes have versions (keys): version id = `tuneId` or `tuneId@Key`. Progress per version: checkpoints `cp`, review `rv`, quiz `qz`.
- Changing data shape? Add a one-time migration in `migrate()` guarded by a flag/revision, and keep old data working.
  Automatic saves (not user edits) use `save(true)` so they don't cause sync conflicts.

## Checking a change
1. Syntax: `sed -n '/<script>/,/<\/script>/p' index.html | sed '1d;$d' > /tmp/app.js && node --check /tmp/app.js`
2. Run it: `python3 -m http.server 8000` and load `http://localhost:8000/` in a headless browser (e.g. Playwright) at
   phone width (~360–390px); click through the feature and check the console for errors.
3. Commit with a clear message, bump the `sw.js` cache version, push to `main`.
