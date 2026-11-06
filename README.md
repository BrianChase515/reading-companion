# Reading Companion

**Read books with Claude, and get the real text, not a remembered paraphrase.**

Reading Companion turns Claude into a reading buddy and thought partner. Tell it "I'm reading Plutarch on the Delay of Divine Justice tonight, want to read it with me?" It opens the same text, finds your place, reads the same pages, and talks about them with you, quoting the actual translation and saying where each line is.

## The problem

Ask an AI about a passage and it answers from memory. Quotes drift, translations get blended, and you can't tell what the book actually says. Reading Companion keeps a real copy of the book next to Claude, so every quote can be checked.

## What it does

- **A local shelf** of public-domain classics from Project Gutenberg, plus any EPUB, PDF, HTML, Markdown or TXT you own, stored as plain Markdown with chapter headings.
- **An optional starter kit** of about 125 classics: Plato, Aristotle, Plotinus, the Stoics, Plutarch, Augustine, Dante, Montaigne, Spinoza, Hume, Kant, Nietzsche, scripture, epic, drama and the great novels. About 120 MB, offered once, downloaded only if you say yes.
- **Search** for an exact phrase, falling back to "these words close together", plus a table of contents.
- **Reading a slice at a time**, so Claude reads exactly what you've read, with bookmarks that persist between sessions.
- **A friend, not a lecturer:** it starts from what struck you, adds one thing you might not have, disagrees when it's warranted, and doesn't spoil what's ahead.

## What it runs, downloads and stores

Reading Companion is one readable Python file, `skills/reading-companion/scripts/shelf.py`, using only the standard library. Claude runs it with `python3` when you ask about a book.

- **Network:** it contacts Project Gutenberg only. It downloads Gutenberg's public catalog file (`gutenberg.org/cache/epub/feeds/pg_catalog.csv`, refreshed at most every 30 days) and book files from Gutenberg's official mirror (`gutenberg.pglaf.org`, changeable with `$PG_MIRROR`), 2 seconds apart, as Gutenberg asks of scripts. It sends no personal data, conversation text or files anywhere. Searching your shelf happens locally.
- **Files:** it writes only inside your shelf folder, `~/ReadingShelf` by default (change it with `$READING_SHELF`): the books as Markdown, `catalog.json`, a human-readable `CATALOG.md`, a bookmarks file and the cached catalog. "Remove" moves a book to `_inbox/removed/` instead of deleting it.
- **Your ebooks:** it reads a file only when you ask it to add that file. PDF import runs the local `pdftotext` program if it's installed. Nothing is uploaded.
- **Copyright:** it only downloads public-domain texts from Gutenberg, and only imports books you already own. It never fetches copyrighted books from anywhere else.

## Where it works best

Claude Code, and other setups where Claude can run Python, reach gutenberg.org and keep files between sessions. In environments without network access you can still add your own ebooks. Where files don't persist, the shelf may need to be rebuilt each session.

## Install

**Claude apps (claude.ai, desktop):** download [`reading-companion.zip`](https://github.com/BrianChase515/reading-companion/raw/downloads/reading-companion.zip) and upload it under Customize > Skills. Then ask Claude to "set up my reading shelf."

**Claude Code**
```
/plugin marketplace add BrianChase515/reading-companion
/plugin install reading-companion@reading-companion
```
Or copy `skills/reading-companion/` into `~/.claude/skills/`.

## Use it without Claude

```
python3 skills/reading-companion/scripts/shelf.py setup --starter
python3 skills/reading-companion/scripts/shelf.py get "consolation of philosophy"
python3 skills/reading-companion/scripts/shelf.py read "consolation" --ch 3
python3 skills/reading-companion/scripts/shelf.py read "consolation" --next
```

## More skills by the same author

[Skill Spotter](https://github.com/BrianChase515/skill-spotter) offers to turn tasks you repeat into skills. [Blindspot](https://github.com/BrianChase515/blindspot) catches the missing context in a vague request before Claude guesses.

## Author

Built by [Brian Chase](https://github.com/BrianChase515). MIT licensed. Texts come from [Project Gutenberg](https://www.gutenberg.org); please respect their [terms of use](https://www.gutenberg.org/policy/terms_of_use.html).
