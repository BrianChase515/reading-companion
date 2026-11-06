# reading-companion

A Claude skill that makes your AI a **reading buddy and thought partner**. Tell it "I'm reading Plutarch on the Delay of Divine Justice tonight, want to read it with me?" It opens the same text, finds your place, reads the same pages, and talks about them, quoting the real translation with locations instead of paraphrasing from memory.

- **A local shelf** of public-domain classics from Project Gutenberg, plus any EPUB, PDF or TXT you own. Books are stored as plain Markdown with chapter headings.
- **An optional starter kit** of about 125 classics: Plato, Aristotle, Plotinus, the Stoics, Plutarch, Augustine, Dante, Montaigne, Spinoza, Hume, Kant, Nietzsche, scripture, epic, drama and the great novels.
- **Search** for an exact phrase, falling back to "these words close together", plus a table of contents, slice-at-a-time reading, and bookmarks that persist between sessions.
- **One Python file, standard library only** (`pdftotext` only for importing PDFs).

Best in Claude Code and local or agent setups where files persist between sessions. In ordinary chat it still works, but the shelf may need to be re-fetched each conversation.

## Install

Copy this folder into your skills directory (for Claude Code, `~/.claude/skills/reading-companion/`), then ask Claude to "set up my reading shelf".

## Use without Claude

```
python3 scripts/shelf.py setup --starter
python3 scripts/shelf.py get "consolation of philosophy"
python3 scripts/shelf.py read "consolation" --ch 3
python3 scripts/shelf.py read "consolation" --next
```

Texts come from [Project Gutenberg](https://www.gutenberg.org). Please respect their terms; the script downloads slowly (2 s apart) on purpose.

MIT licence.
