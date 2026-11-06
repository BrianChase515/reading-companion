# Reading Companion

**Read books with Claude, and get the real text, not a remembered paraphrase.**

Reading Companion turns Claude into a reading buddy and thought partner. Tell it "I'm reading Plutarch on the Delay of Divine Justice tonight, want to read it with me?" It opens the same text, finds your place, reads the same pages, and talks about them with you, quoting the actual translation and saying where each line is.

## The problem

Ask an AI about a passage and it answers from memory. Quotes drift, translations get blended, and you can't tell what the book actually says. Reading Companion keeps a real copy of the book next to Claude, so every quote can be checked.

## What it does

- **A local shelf** of public-domain classics from Project Gutenberg, plus any EPUB, PDF, HTML, Markdown or TXT you own, stored as plain text you can open yourself.
- **An optional starter kit** of about 125 classics: Plato, Aristotle, Plotinus, the Stoics, Plutarch, Augustine, Dante, Montaigne, Spinoza, Hume, Kant, Nietzsche, scripture, epic, drama and the great novels. About 120 MB, offered once, downloaded only if you say yes.
- **Search** for an exact phrase, falling back to "these words close together", plus a table of contents.
- **Reading a slice at a time**, so Claude reads exactly what you've read, with bookmarks that persist between sessions.
- **A friend, not a lecturer:** it starts from what struck you, adds one thing you might not have, disagrees when it's warranted, and doesn't spoil what's ahead.

## Two editions

- **Directory edition (this branch, `main`):** instructions only. Claude does everything with standard shell commands (`curl`, `grep`, `sed`, `awk`) on plain text files. This is the version in Anthropic's Claude directory.
- **Full edition ([`full` branch](https://github.com/BrianChase515/reading-companion/tree/full)):** the same skill plus `shelf.py`, a small standard-library Python tool that converts Gutenberg's HTML with clean chapter headings, imports EPUBs properly, and searches across the whole shelf in one command.

## What it runs, downloads and stores

- **Network:** Project Gutenberg only. It downloads Gutenberg's public catalog file (`gutenberg.org/cache/epub/feeds/pg_catalog.csv`, refreshed at most every 30 days) and book files from Gutenberg's official mirror (`gutenberg.pglaf.org`), one at a time and 2 seconds apart in bulk, as Gutenberg asks of scripts. It never scrapes Gutenberg's website and sends no personal data, conversation text or files anywhere.
- **Files:** it writes only inside your shelf folder, `~/ReadingShelf` by default (change it with `$READING_SHELF`): the books as plain text, `CATALOG.md`, `BOOKMARKS.md` and the cached catalog.
- **Your ebooks:** it reads a file only when you ask it to add that file. For a PDF it uses the local `pdftotext` tool, if you have it. Nothing is uploaded.
- **Copyright:** it only downloads public-domain texts from Gutenberg, and only imports books you already own. It never fetches copyrighted books from anywhere else.

## Where it works best

Claude Code and other setups where Claude can run shell commands, reach gutenberg.org and keep files between sessions. Without network access you can still add your own ebooks. Without a shell, paste or upload the text and Claude reads along from that.

## Install

**From the Claude directory:** find Reading Companion and add it.

**Claude apps, full edition:** download [`reading-companion.zip`](https://github.com/BrianChase515/reading-companion/raw/downloads/reading-companion.zip) and upload it under Customize > Skills. Then ask Claude to "set up my reading shelf."

**Claude Code**
```
/plugin marketplace add BrianChase515/reading-companion
/plugin install reading-companion@reading-companion
```
Or copy `skills/reading-companion/` from either branch into `~/.claude/skills/`.

## Use the full edition's tool without Claude

From the `full` branch:
```
python3 skills/reading-companion/scripts/shelf.py setup --starter
python3 skills/reading-companion/scripts/shelf.py get "consolation of philosophy"
python3 skills/reading-companion/scripts/shelf.py read "consolation" --ch 3
```

## More skills by the same author

[Skill Spotter](https://github.com/BrianChase515/skill-spotter) offers to turn tasks you repeat into skills. [Blindspot](https://github.com/BrianChase515/blindspot) catches the missing context in a vague request before Claude guesses.

## Author

Built by [Brian Chase](https://github.com/BrianChase515). MIT licensed. Texts come from [Project Gutenberg](https://www.gutenberg.org); please respect their [terms of use](https://www.gutenberg.org/policy/terms_of_use.html).
