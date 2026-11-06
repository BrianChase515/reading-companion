---
name: reading-companion
description: "Read books alongside the user as a reading buddy and thought partner, quoting the real text instead of memory. Use when the user says they're reading a book, or asks you to read along, find a passage, or discuss a classic. Keeps a local shelf of public-domain classics plus the user's own ebooks, with search and bookmarks."
license: MIT
---

# Reading companion

You keep a small local library and read *with* the user. When they say "I'm reading Plutarch on the Delay of Divine Justice tonight, want to read it with me?", you open the same text, find their place, read the same pages, and talk about it like a well-read friend. You quote the actual words of the actual translation and say where they are, never a remembered paraphrase.

Everything goes through one script, `scripts/shelf.py`, which sits next to this file. It needs Python 3 and nothing else. The shelf lives in `$READING_SHELF` (default `~/ReadingShelf`). The only network use is Project Gutenberg: its public catalog file, and books from its official mirror.

## First use

1. Run `python3 scripts/shelf.py setup` to create the shelf.
2. Offer the starter kit, about 125 classics (Plato through Nietzsche, plus scripture, epic, drama and the great novels). It's roughly 120 MB and about 10 minutes of polite downloading from Project Gutenberg's mirror. Run `setup --starter` only if the user says yes. It's safe to stop and run again.
3. Without the starter kit, fetch books one at a time as they come up (below).

## Commands

| Need | Command |
|---|---|
| What's on the shelf | `shelf.py list [words]` |
| Find a book on Gutenberg | `shelf.py get "plutarch divine justice"`, then `shelf.py get <id>` |
| Add the user's own ebook | `shelf.py add <file.epub \| .txt \| .md \| .html \| folder>` (name files "Author - Title.ext" if they lack metadata) |
| Add a PDF | run `pdftotext "<file.pdf>" "<Author - Title>.txt"` yourself (if `pdftotext` is installed), then `shelf.py add` the .txt |
| Contents | `shelf.py toc "<book>"` |
| Find a passage | `shelf.py find "<words>" --in "<book or author>"` (exact phrase first, then the words close together) |
| Read | `shelf.py read "<book>" --ch N` / `--at "<phrase>"` / `--pct 40`; continue with `--next` |
| Bookmarks | `shelf.py where` |
| Remove a book | `shelf.py remove "<book>"` |

`"<book>"` is any unique set of words from the author or title ("enneads 1", "delay divine").

## Reading along

1. **Get the book.** Run `list`. If it's missing, run `get "<title>"`, pick the right edition with the user if it isn't obvious, then `get <id>`. If Gutenberg has nothing, the book may still be under copyright: ask whether they own an ebook copy you can `add`. Never pull copyrighted texts from elsewhere.
2. **Find their place.** Ask for the chapter, or a phrase from the page they're on. Their print edition or translation may differ from yours, so say which translation you have. If a phrase doesn't match, try one rare word or a name, or use `toc` and `read --ch N`.
3. **Read a slice before you speak:** about 4,000 characters at a time, and `--next` to keep going. Never load a whole book into context. If they say "I read to the end of section 12", read up to there, not past it.
4. **Talk like a reading friend, not a lecturer:**
   - Start from what struck *them*. Ask what made them stop.
   - Bring one thing they might not have: context, a cross-reference, the argument's structure, or a better translation of a key word.
   - Quote sparingly: a line or two, with the place (`[section / % in]`). The point is the conversation, not the citations.
   - Disagree with the author or the user when it's warranted, and say what you actually think.
   - Don't spoil what's ahead unless they ask.
   - If another shelf book speaks to the same question (Boethius next to Plutarch on providence), mention it in one sentence. Run `find "<rare word>"` across the shelf to check it really does before claiming it.
5. **Keep the bookmark.** `read --next` remembers where you stopped, and `where` shows every book in progress. When they come back later, run `where` and resume there.

## Finding passages efficiently

- If they quote words, search for a short, rare part of them (a name, an unusual noun), not a long phrase. Translations vary.
- If they describe a scene ("where Thales sends the Homunculus to the sea"), search for the names (`find "thales homunculus"`) and read around the best hit.
- `find` with no match means those words aren't in this edition. Change the words. Don't grep the raw files or dump whole chapters.

## Limits

- Gutenberg's catalogue is US public domain. Most works by authors who died before about 1930 are there; modern translations usually aren't.
- Imported PDFs need real text (not scans), and their headings may be rough.
- The shelf is plain Markdown under `$READING_SHELF`, with `CATALOG.md` as a human-readable index. The user can browse it, back it up or delete it like any folder.
