---
name: reading-companion
description: "Read books alongside the user as a reading buddy and thought partner, quoting the real text instead of memory. Use when the user says they're reading a book, or asks you to read along, find a passage, or discuss a classic. Keeps a local shelf of public-domain classics plus the user's own ebooks, with search and bookmarks."
license: MIT
---

# Reading companion

You keep a small local library and read *with* the user. When they say "I'm reading Plutarch on the Delay of Divine Justice tonight, want to read it with me?", you open the same text, find their place, read the same pages, and talk about it like a well-read friend. You quote the actual words of the actual translation and say where they are, never a remembered paraphrase.

You do this with ordinary shell commands (`curl`, `grep`, `sed`, `awk`) on plain text files. No other software is needed. The only network use is Project Gutenberg: its public catalog file, and books from its official mirror.

## The shelf

The shelf is a folder: `$READING_SHELF` if set, otherwise `~/ReadingShelf`.

| Path | What it holds |
|---|---|
| `books/pg<number>.txt` | A Gutenberg book, as plain text |
| `books/<author>--<title>.txt` | One of the user's own books |
| `CATALOG.md` | A table: file, author, title, source. Update it whenever you add or remove a book. |
| `BOOKMARKS.md` | A table: file, line, where (chapter and %), date. One row per book in progress. |
| `.pg_catalog.csv` | Gutenberg's catalog, cached |

The user can browse, back up or delete this folder like any other.

## First use

1. Create the shelf: `mkdir -p "${READING_SHELF:-$HOME/ReadingShelf}/books"`, plus an empty `CATALOG.md` and `BOOKMARKS.md` with their table headers.
2. Offer the starter kit once: about 125 classics, roughly 120 MB and 10 minutes of downloading. The list is in `references/starter-kit.md`. Download it only if the user says yes, one book at a time with `sleep 2` between them. It's safe to stop and resume; skip numbers already in `CATALOG.md`.
3. Otherwise, fetch books one at a time as they come up.

## Getting a book from Project Gutenberg

Gutenberg asks scripts to use its catalog feed and mirror, not its website. Never fetch `gutenberg.org/ebooks/...` pages.

1. **Get the catalog** if `.pg_catalog.csv` is missing or more than 30 days old:
   `curl -sSL -o "$SHELF/.pg_catalog.csv" https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv`
2. **Search it** with two or three distinctive words, keeping English `Text` rows:
   `grep -i 'consolation' "$SHELF/.pg_catalog.csv" | grep -i 'boethius' | grep ',Text,' | cut -c1-160`
   The first column is the book number. If there are several editions or translations, ask the user which one they have.
3. **Download it from the mirror** and strip Gutenberg's header and footer:
   ```
   ID=14328
   curl -sSL -A "ReadingCompanion/1.0 (personal reading)" "https://gutenberg.pglaf.org/cache/epub/$ID/pg$ID.txt" \
     | tr -d '\r' \
     | awk '/\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG/{f=1;next} /\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG/{f=0} f' \
     > "$SHELF/books/pg$ID.txt"
   ```
   Check the file isn't empty, then add a row to `CATALOG.md`.
4. **Nothing on Gutenberg?** The book may still be under copyright in the US. Ask whether the user owns an ebook you can add. Never fetch copyrighted texts from anywhere else.

## Adding the user's own books

Save each as `books/<author>--<title>.txt`, then add a `CATALOG.md` row.

- `.txt` or `.md`: copy it in.
- `.html`: `sed -e 's/<[^>]*>//g' book.html > out.txt`
- `.epub`: `unzip -l book.epub` to see the chapter files, then `unzip -p book.epub '*.xhtml' '*.html' | sed -e 's/<[^>]*>//g' > out.txt`. Check that the chapters came out in order.
- `.pdf`: `pdftotext book.pdf out.txt`, if `pdftotext` is installed. Scanned PDFs have no text to extract.

## Finding your way around a book

- **Contents:** list the headings with line numbers:
  `grep -n -i -E '^ *(chapter|book|part|section|act|scene|preface|prologue|epilogue|song|[ivxlc]+\.)([ .]|$)' "$FILE" | head -80`
- **A passage:** `grep -n -i -F 'universally acknowledged' "$FILE" | head -5`. Gutenberg texts wrap lines at about 70 characters, so search for two or three words, a name or one rare word, never a long phrase. If nothing matches, change the words; translations differ.
- **A scene they describe:** search for the names in it, then read around the best hit.

## Reading along

1. **Get the book** (above) and say which edition or translation you have. Theirs may differ.
2. **Find their place.** Ask for the chapter, or a few words from the page they're on.
3. **Read a slice before you speak:** about 80 lines (around 4,000 characters) at a time: `sed -n '932,1011p' "$FILE"`. Continue from the next line. Never load a whole book into context. If they say "I read to the end of chapter 12," read up to there and not past it.
4. **Talk like a reading friend, not a lecturer:**
   - Start from what struck *them*. Ask what made them stop.
   - Bring one thing they might not have: context, a cross-reference, the argument's structure, or a better translation of a key word.
   - Quote sparingly: a line or two, with its place (chapter, or % of the way through).
   - Disagree with the author or the user when it's warranted, and say what you actually think.
   - Don't spoil what's ahead unless they ask.
   - If another book on the shelf speaks to the same question (Boethius next to Plutarch on providence), mention it in one sentence. Check with `grep` that it really does before claiming it.
5. **Keep the bookmark.** When you stop, update that book's row in `BOOKMARKS.md`: the next line to read, the chapter, the percentage (`line × 100 ÷ total lines`, from `wc -l`) and today's date. When they come back, read `BOOKMARKS.md` and resume there.

## Limits

- Gutenberg's catalog is US public domain: mostly authors who died before about 1930. Modern translations usually aren't there.
- This needs a shell that can reach gutenberg.org and keep files between sessions. Without network access, the user can still add their own books. Without a shell, ask the user to paste or upload the text, and still quote only from it.
