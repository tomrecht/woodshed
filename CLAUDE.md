# Woodshed – sax practice tracker

Personal web app (installable PWA) for tracking saxophone practice. Live at https://tomrecht.github.io/woodshed/ –
GitHub Pages serves the `main` branch as-is, so **a push to `main` is a deploy**. There is no build step.

The owner plays alto sax and often asks for changes from their phone. Keep replies short and say plainly what changed.

## Files
- `index.html` – the whole app: CSS, HTML shell and one `<script>` (vanilla JS, no framework, no dependencies).
- `sw.js` – offline cache. **Bump `CACHE` (`woodshed-vN`) on every deploy**, or phones keep the old version.
  New static files must be added to its `FILES` list.
- `library.json` – ~1,355 chord charts (iReal Pro), as **E♭ (alto) parts**: `{t: title, s: style, c: composer, k: key, ts, b: [bar]}`;
  a bar is `{n, c: [chord symbols], sec?, ro?/rc? (repeat open/close), end? (ending no.), rep? (% bar), mk? (Segno/Coda/D.C.)}`.
- `licks/` lick images, `piano/` Salamander piano samples (CC BY 3.0), `drums/` VCSL drum samples (CC0).
- `tools/ireal_decode.py`, `tools/add_chart.py` – decode iReal Pro forum share links and add a chart to `library.json`
  (converts concert → alto). Forum: https://forums.irealpro.com (XenForo; search with `/search/search?keywords=...`).
- PDFs (the owner's iReal export and lick sheets) are git-ignored and not in the repo.

## Data – never lose the owner's data
- All state lives in `localStorage` key `woodshed.v1` (object `S`), optionally synced to a private GitHub gist.
  Lick photos the user adds live in IndexedDB and sync to the gist as a separate file (`woodshed-images.json`).
- `S.lib` = shared library (sections → exercises, licks, tunes); `S.prog[instrumentId]` = per-instrument progress
  (`bpm`, `hist`, `sessions`, `tunes`, `touched`, `badges`, …).
- `S.sched` = scheduled practice (once, or weekly on chosen days; optional length; phone reminders via ntfy.sh, settings per device in `woodshed.ntfy`); `S.ear` = shared ear-training stats;
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
