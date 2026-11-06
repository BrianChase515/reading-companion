#!/usr/bin/env python3
"""
shelf.py - a local bookshelf an AI can actually read from: public-domain classics from Project Gutenberg
(plus any EPUB/PDF/TXT you own), stored as Markdown, searchable, with bookmarks. Standard library only
(PDF import also needs `pdftotext`).

Shelf folder: $READING_SHELF, or ~/ReadingShelf. Books download from Gutenberg's mirror ($PG_MIRROR).

  shelf.py setup [--starter]          create the shelf; --starter downloads the ~125-book starter kit (~120 MB, ~10 min)
  shelf.py list [words]               what's on the shelf (filter by author/title words)
  shelf.py get "<title or author>"    search Project Gutenberg (English) -> numbered matches
  shelf.py get <id> [<id> ...]        download those Gutenberg books onto the shelf
  shelf.py add <file|folder>          import your own EPUB / HTML / TXT / MD / PDF ("Author - Title.ext" helps)
  shelf.py toc "<book>"               chapters/sections, numbered
  shelf.py find "<words>" [--in "<book or author>"] [--n 5]
                                      exact phrase; if none, all the words close together
  shelf.py read "<book>" [--ch N | --at "<phrase>" | --next | --pct 40] [--chars 4000]
                                      a slice of the text; --next continues from your bookmark
  shelf.py where                      bookmarks: where you are in each book
  shelf.py remove "<book>"            take a book off the shelf

"<book>" is any unique set of words from the author/title ("plotinus enneads 1", "delay divine").
"""
import os, sys, re, json, csv, time, html, zipfile, shutil, subprocess, posixpath, unicodedata, urllib.request
from html.parser import HTMLParser

LIB = os.path.expanduser(os.environ.get("READING_SHELF", "~/ReadingShelf"))
CAT = os.path.join(LIB, "catalog.json"); PGCAT = os.path.join(LIB, ".pg_catalog.csv"); POS = os.path.join(LIB, ".bookmarks.json")
UA = {"User-Agent": "ReadingShelf/1.0 (personal reading; polite)"}
# Books come from Project Gutenberg's official mirror, as Gutenberg asks of scripts (gutenberg.org/policy/robot_access.html).
MIRROR = os.environ.get("PG_MIRROR", "https://gutenberg.pglaf.org").rstrip("/")
STARTER = [  # ~125 Project Gutenberg ids: philosophy, history, scripture, epic, drama, novels
 1497,1600,1658,1656,1636,1572,1750,1643,1672,1726, 8438,6762,1974,2412, 42930,42931,42932,
 45109,10661,2680,3794,674,23639,58567,785,2808,54161,57342,14328,
 2707,2456,7142,2199,1727,348,8714,31,35451,2562,228,21765,26073,
 3296,45304,45305,17611,8800,1232,10827,2130,9371,3600,575,45988,
 3207,59,70091,3800,989,18269,7370,10615,17147,4723,4705,9662,4583,46333,11136,5427,3913,19942,
 4280,5682,5683,55108,38427,11945,60333,1998,4363,52319,51356,52263,34901,11224,2944,205,61,3300,3420,621,5116,
 10,2388,216,3330,2017,11000,
 100,996,20,3023,28054,2554,600,2600,2701,829,2383,731,1399,1342,84,345,43,5200,1184,135,2591,1080,1260,4300,10007,2542]

def arg(n, d):
    a = sys.argv
    if n in a:
        i = a.index(n)
        if i + 1 < len(a): v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d

def flag(n):
    if n in sys.argv: sys.argv.remove(n); return True
    return False

def cat():
    try: return json.load(open(CAT))
    except Exception: return []

def save_cat(c):
    os.makedirs(LIB, exist_ok=True); tmp = CAT + ".tmp"
    json.dump(c, open(tmp, "w"), indent=1, ensure_ascii=False); os.replace(tmp, CAT)
    with open(os.path.join(LIB, "CATALOG.md"), "w") as f:
        f.write("# Reading shelf (%d books)\n\n" % len(c))
        for b in sorted(c, key=lambda b: (b["author"], b["title"])): f.write("- %s — *%s*  (`%s`)\n" % (b["author"], b["title"], b["file"]))

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60] or "untitled"

def bookmarks():
    try: return json.load(open(POS))
    except Exception: return {}

# ---------- converters
class H2M(HTMLParser):
    """HTML -> Markdown. Headings are collected whole, so <br>, <img> or <span> inside a title can't split it."""
    def __init__(s): super().__init__(); s.o = []; s.skip = 0; s.h = None
    def handle_starttag(s, t, a):
        if t in ("script", "style", "head"): s.skip += 1
        elif t in ("h1", "h2", "h3", "h4"): s.h = []
        elif s.h is not None: s.h.append(" ")
        elif t in ("p", "div", "blockquote", "li", "tr"): s.o.append("\n\n")
        elif t == "br": s.o.append("\n")
    def handle_endtag(s, t):
        if t in ("script", "style", "head"): s.skip = max(0, s.skip - 1)
        elif t in ("h1", "h2", "h3", "h4") and s.h is not None:
            title = re.sub(r"\s+", " ", "".join(s.h)).strip(); s.h = None
            s.o.append("\n\n## %s\n\n" % title if title else "\n\n")
    def handle_data(s, d):
        if s.skip: return
        if s.h is not None: s.h.append(d)
        else: s.o.append(d)
    def text(s):
        t = "".join(s.o).replace("\xa0", " "); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()

def html_md(h): p = H2M(); p.feed(h); return p.text()

def strip_pg(t):
    a = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n", t)
    b = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK", t)
    return t[a.end() if a else 0: b.start() if b else len(t)].strip()

def epub_md(path):
    z = zipfile.ZipFile(path); names = z.namelist()
    opf = re.search(r'full-path="([^"]+)"', z.read("META-INF/container.xml").decode("utf-8", "replace")).group(1)
    o = z.read(opf).decode("utf-8", "replace"); base = posixpath.dirname(opf)
    t = re.search(r"<dc:title[^>]*>(.*?)</dc:title>", o, re.S); c = re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>", o, re.S)
    man = dict(re.findall(r'<item\b[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', o))
    man.update({i: h for h, i in re.findall(r'<item\b[^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', o)})
    parts = []
    for idref in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', o):
        f = posixpath.normpath(posixpath.join(base, urllib.request.unquote(man.get(idref, ""))))
        if f in names: parts.append(html_md(z.read(f).decode("utf-8", "replace")))
    clean = lambda m: html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
    return clean(t), clean(c), "\n\n".join(parts)

def same_author(c, author):
    w = set(re.findall(r"[a-z]{3,}", author.lower()))
    for b in c:
        w2 = set(re.findall(r"[a-z]{3,}", b["author"].lower()))
        if w and w2 and (w <= w2 or w2 <= w): return b["author"]
    return author

def shelve(title, author, body, source, gid=None):
    c = cat(); author = same_author(c, html.unescape(author or "Anonymous").strip()); title = html.unescape(title or "Untitled").strip()
    fn = os.path.join(slug(author), slug(title) + ".md")
    if any(b["file"] == fn for b in c): print("already on the shelf: %s — %s" % (author, title)); return
    os.makedirs(os.path.join(LIB, slug(author)), exist_ok=True)
    body = re.sub(r"^#{1,6}[ \t]+(?=\S)", "## ", body, flags=re.M)   # every heading level becomes a section
    md = "# %s\n\n*%s* — %s\n\n---\n\n%s\n" % (title, author, source, body.strip())
    open(os.path.join(LIB, fn), "w", encoding="utf-8").write(md)
    c.append({"id": gid, "author": author, "title": title, "file": fn, "kb": len(md) // 1024}); save_cat(c)
    print("shelved: %s — %s  (%d KB, %d sections)" % (author, title, len(md) // 1024, md.count("\n## ")))

# ---------- Gutenberg
def fetch(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read().decode("utf-8", "replace")
    except Exception: return None

def pg_rows():
    if not os.path.exists(PGCAT) or time.time() - os.path.getmtime(PGCAT) > 30 * 86400:
        os.makedirs(LIB, exist_ok=True)
        d = urllib.request.urlopen(urllib.request.Request("https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv", headers=UA), timeout=180).read()
        open(PGCAT, "wb").write(d)
    return [r for r in csv.DictReader(open(PGCAT, encoding="utf-8")) if r["Type"] == "Text" and "en" in r["Language"]]

def clean_author(a): return re.sub(r",\s*(\d|\?|BCE|active|fl\.).*$", "", a.split(";")[0]).strip()

def download(gid, rows):
    if any(str(b.get("id")) == str(gid) for b in cat()): print("already on the shelf: #%s" % gid); return
    r = next((r for r in rows if r["Text#"] == str(gid)), None)
    if not r: print("no English Gutenberg text #%s" % gid); return
    title, author, src = re.sub(r"\s+", " ", r["Title"]).strip(), clean_author(r["Authors"]) or "Anonymous", "Project Gutenberg #%s" % gid
    h = fetch("%s/cache/epub/%s/pg%s-images.html" % (MIRROR, gid, gid))   # HTML keeps real chapter headings
    if h:
        body = strip_pg(html_md(re.sub(r'<span class="pagenum">.*?</span>', "", h, flags=re.S)))
        if len(body) > 2000: return shelve(title, author, body, src, int(gid))
    raw = fetch("%s/cache/epub/%s/pg%s.txt" % (MIRROR, gid, gid))
    if not raw: print("couldn't download #%s" % gid); return
    shelve(title, author, strip_pg(raw), src, int(gid))

# ---------- reading
def pick(c, key):
    ws = key.lower().split(); m = [b for b in c if all(w in (b["author"] + " " + b["title"] + " " + b["file"]).lower() for w in ws)]
    ex = [b for b in m if b["title"].lower() == key.lower()]
    if len(m) > 1 and len(ex) == 1: m = ex
    if len(m) != 1:
        print("%d books match %r%s" % (len(m), key, (": " + "; ".join("%s — %s" % (b["author"], b["title"]) for b in m[:8])) if m else " (shelf.py list, or shelf.py get to fetch it)"))
        sys.exit(2)
    return m[0]

def load(b): return open(os.path.join(LIB, b["file"]), encoding="utf-8").read()
def heads(t): return [(m.start(), m.group(1)) for m in re.finditer(r"^## (.+)$", t, re.M)]

def main():
    a = sys.argv
    if len(a) < 2: print(__doc__); return
    cmd = a[1]; c = cat()
    if cmd == "setup":
        os.makedirs(os.path.join(LIB, "_inbox"), exist_ok=True); save_cat(c); print("shelf: %s" % LIB)
        if flag("--starter"):
            rows = pg_rows(); have = {str(b.get("id")) for b in c}
            todo = [g for g in STARTER if str(g) not in have]
            print("downloading %d books (2 s apart; safe to interrupt and re-run)…" % len(todo))
            for k, g in enumerate(todo):
                if k: time.sleep(2)
                download(g, rows)
    elif cmd == "list":
        q = " ".join(a[2:]).lower()
        bs = [b for b in c if all(w in (b["author"] + " " + b["title"]).lower() for w in q.split())]
        for b in sorted(bs, key=lambda b: (b["author"], b["title"])): print("%-28s %s" % (b["author"][:28], b["title"][:80]))
        print("(%d books · %s)" % (len(bs), LIB))
    elif cmd == "get":
        q = a[2:]
        if not q: print(__doc__); return
        if all(x.isdigit() for x in q):
            rows = pg_rows()
            for k, g in enumerate(q):
                if k: time.sleep(2)
                download(g, rows)
            return
        rows = pg_rows(); ql = " ".join(q).lower()
        m = [r for r in rows if all(w in (r["Title"] + " " + r["Authors"]).lower() for w in ql.split())][:15]
        for r in m: print("#%-6s %s — %s" % (r["Text#"], clean_author(r["Authors"])[:30], re.sub(r"\s+", " ", r["Title"])[:90]))
        print("(%d shown) → shelf.py get <id>" % len(m) if m else "nothing on Gutenberg for %r - it may not be public domain in the US; if the user owns a copy, shelf.py add <file>" % ql)
    elif cmd == "add":
        src = a[2] if len(a) > 2 else os.path.join(LIB, "_inbox")
        files = [src] if os.path.isfile(src) else [os.path.join(src, f) for f in sorted(os.listdir(src)) if not f.startswith(".") and os.path.isfile(os.path.join(src, f))]
        for f in files:
            ext = f.lower().rsplit(".", 1)[-1]; name = os.path.splitext(os.path.basename(f))[0]
            ga, _, gt = name.partition(" - ") if " - " in name else ("", "", name)
            try:
                if ext == "epub": t, au, body = epub_md(f); shelve(t or gt, au or ga, strip_pg(body), "from " + os.path.basename(f))
                elif ext in ("html", "htm", "xhtml"): shelve(gt, ga, html_md(open(f, encoding="utf-8", errors="replace").read()), "from " + os.path.basename(f))
                elif ext in ("txt", "md"): raw = open(f, encoding="utf-8", errors="replace").read(); shelve(gt, ga, strip_pg(raw), "from " + os.path.basename(f))
                elif ext == "pdf":
                    if not shutil.which("pdftotext"): print("skip %s: PDF needs pdftotext (poppler)" % f); continue
                    shelve(gt, ga, subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout, "from " + os.path.basename(f))
                else: print("skip %s (.%s)" % (f, ext))
            except Exception as e: print("failed %s: %s" % (f, e))
    elif cmd == "toc":
        b = pick(c, a[2]); hs = heads(load(b))
        for i, (_, h) in enumerate(hs, 1): print("%3d  %s" % (i, h[:100]))
        print("(%d sections — read with --ch N)" % len(hs))
    elif cmd == "find":
        scope = arg("--in", "").lower(); n = arg("--n", 5); q = " ".join(a[2:]).lower(); hits = 0
        books = [b for b in c if all(w in (b["author"] + " " + b["title"] + " " + b["file"]).lower() for w in scope.split())]
        def show(b, t, i, j, tag=""):
            ch = [h for p, h in heads(t) if p < i]; s = re.sub(r"\s+", " ", t[max(0, i - 250): j + 250])
            print("— %s, %s%s  [%d%% in]%s\n  …%s…\n" % (b["author"], b["title"][:60], (" · " + ch[-1][:50]) if ch else "", 100 * i // max(1, len(t)), tag, s))
        for b in books:
            t = load(b); lo = t.lower(); i = lo.find(q)
            while i >= 0 and hits < n: show(b, t, i, i + len(q)); hits += 1; i = lo.find(q, i + len(q))
            if hits >= n: break
        if not hits:
            ws = [w for w in re.findall(r"[a-z']{3,}", q) if w not in ("the", "and", "that", "with", "for", "his", "her", "was", "are")]
            if len(ws) >= 2:
                for b in books:
                    t = load(b); lo = t.lower()
                    for m in re.finditer(re.escape(ws[0]), lo):
                        win = lo[max(0, m.start() - 300): m.start() + 300]
                        if all(w in win for w in ws[1:]): show(b, t, m.start(), m.end(), "  (words close together)"); hits += 1
                        if hits >= n: break
                    if hits >= n: break
        print("%d passage(s)." % hits if hits else "No match. Try one rare word or a name, or toc + read.")
    elif cmd == "read":
        nxt = flag("--next"); b = pick(c, a[2]); ch = arg("--chars", 4000); at = arg("--at", ""); chn = arg("--ch", 0); pct = arg("--pct", -1.0)
        t = load(b); pos = bookmarks()
        if nxt: start = pos.get(b["file"], 0)
        elif at:
            i = t.lower().find(at.lower())
            if i < 0: print("%r isn't in %s. Try shelf.py find." % (at, b["title"])); sys.exit(2)
            start = max(0, t.rfind("\n\n", 0, max(0, i - ch // 5)) + 2)
        elif chn:
            hs = heads(t)
            if not 1 <= chn <= len(hs): print("section %d? it has %d (shelf.py toc)" % (chn, len(hs))); sys.exit(2)
            start = hs[chn - 1][0]
        elif pct >= 0: start = int(len(t) * pct / 100)
        else: start = 0
        end = min(len(t), start + ch)
        if end < len(t):                                   # stop at a paragraph, else a line, else a space
            for sep in ("\n\n", "\n", " "):
                k = t.rfind(sep, start + ch // 2, end)
                if k > 0: end = k; break
        pos[b["file"]] = end; json.dump(pos, open(POS, "w"))
        here = [h for p, h in heads(t) if p <= start]
        print("%s — %s  [%d%%→%d%%]%s\n\n%s\n\n(next: shelf.py read \"%s\" --next)" % (b["author"], b["title"], 100 * start // max(1, len(t)),
              100 * end // max(1, len(t)), ("  · " + here[-1][:60]) if here else "", t[start:end].strip(), a[2]))
    elif cmd == "where":
        pos = bookmarks()
        for b in c:
            if b["file"] in pos:
                n = len(load(b)); print("%3d%%  %s — %s" % (100 * pos[b["file"]] // max(1, n), b["author"][:28], b["title"][:60]))
        if not pos: print("no bookmarks yet")
    elif cmd == "remove":
        b = pick(c, a[2]); done = os.path.join(LIB, "_inbox", "removed"); os.makedirs(done, exist_ok=True)
        if os.path.exists(os.path.join(LIB, b["file"])): shutil.move(os.path.join(LIB, b["file"]), os.path.join(done, os.path.basename(b["file"])))
        save_cat([x for x in c if x is not b]); print("removed %s — %s (file kept in _inbox/removed/)" % (b["author"], b["title"]))
    else: print(__doc__)

if __name__ == "__main__":
    main()
