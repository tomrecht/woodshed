# Crossing the Bridge – clarinet exercise book

Builds `books/Crossing-the-Bridge-Clarinet.pdf` (50 exercises over the clarinet break, written pitch).
Run these from this folder:

    python3 gen.py      # exercises -> ex.json (ABC notation)
    python3 page.py     # -> book.html (renders with ../../vendor/abcjs)
    node pdf.js "$PWD/book.html" "$PWD/../../books/Crossing-the-Bridge-Clarinet.pdf"   # Playwright print

`ex.json` and `book.html` are build outputs and are not committed.

The app's "Clarinet: crossing the bridge" category uses the same exercises: `python3 app_data.py > cb.js` prints the
`const CLAR_BRIDGE = …;` line (bars regrouped 5 to a line) to paste over the one in `index.html`.
