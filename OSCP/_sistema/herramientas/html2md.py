#!/usr/bin/env python3
"""
html2md.py — Convierte un writeup de 0xdf (Jekyll + Rouge) a markdown limpio.

Objetivo: corpus de texto BUSCABLE. El valor esta en que:
  1. Los bloques de codigo sobrevivan intactos (ahi viven los comandos buscables).
  2. Los metadatos (maquina, dificultad, SO, fecha) salgan como frontmatter,
     para poder filtrar por ellos.

Uso:
    python3 html2md.py archivo.html              # a stdout
    python3 html2md.py archivo.html -o out.md    # a archivo
"""
import re
import sys
import json
from bs4 import BeautifulSoup, NavigableString, Tag, Comment, Doctype

SITE = "https://0xdf.gitlab.io"


# --------------------------------------------------------------------------
# Metadatos
# --------------------------------------------------------------------------
def extract_metadata(soup, url=""):
    """Extrae los metadatos de la tarjeta htb-card."""
    meta = {
        "maquina": "",
        "dificultad": "",
        "os": "",
        "release": "",
        "retire": "",
        "creadores": "",
        "plataforma": "",
        "htb_url": "",
        "app_url": "",
        "url": url,
    }

    # Nombre de la maquina
    name = soup.select_one("a.htb-box-name")
    if name:
        meta["maquina"] = name.get_text(strip=True)
    else:
        h1 = soup.find("h1")
        if h1:
            meta["maquina"] = re.sub(r"^HTB:\s*", "", h1.get_text(strip=True))

    # Dificultad (del class diff-XXXX)
    badge = soup.select_one("div.htb-difficulty-badge")
    if badge:
        for cls in badge.get("class", []):
            if cls.startswith("diff-"):
                meta["dificultad"] = cls[len("diff-"):]
        if not meta["dificultad"]:
            meta["dificultad"] = badge.get_text(strip=True)

    # Link a HTB
    if name and name.get("href"):
        meta["htb_url"] = name["href"]

    # Pares label/valor (Release Date, Retire Date, OS)
    for item in soup.select("div.htb-meta-item"):
        lab = item.select_one("span.htb-meta-label")
        val = item.select_one("span.htb-meta-value")
        if not lab or not val:
            continue
        label = lab.get_text(strip=True).lower()
        value = re.sub(r"\s+", " ", val.get_text(" ", strip=True))
        if "release" in label:
            meta["release"] = value
        elif "retire" in label:
            meta["retire"] = value
        elif label == "os":
            meta["os"] = value

    # Creadores: viven en div.htb-card-row, no en htb-meta-item
    for rw in soup.select("div.htb-card-row"):
        lab = rw.select_one("span.htb-card-label")
        if lab and "creator" in lab.get_text(strip=True).lower():
            names = [t.get_text(strip=True) for t in rw.select("span.user-text")]
            if not names:
                names = [a.get_text(strip=True) for a in rw.select("a")
                         if a.get_text(strip=True) and not a.find("img")]
            meta["creadores"] = ", ".join(n for n in names if n)

    # Link a la app de HTB (vive en un comentario HTML)
    for cm in soup.find_all(string=lambda t: isinstance(t, str) and "app.hackthebox.com/machines" in t):
        m = re.search(r"https://app\.hackthebox\.com/machines/\d+", cm)
        if m:
            meta["app_url"] = m.group(0)
            break

    # Plataforma: derivada de la URL, NO del class (platform-vulnlab es un
    # class residual y engana: se aplica a maquinas de HTB).
    low_url = (url or "").lower()
    if "hackthebox.com/machines" in meta["htb_url"] or "/htb-" in low_url:
        meta["plataforma"] = "htb"
    elif "vulnlab" in low_url or "vl-" in low_url:
        meta["plataforma"] = "vulnlab"
    else:
        # NO asumir htb: hay posts que no son de una maquina (notas, modulos,
        # home lab). Marcarlos como htb ensuciaria cualquier filtro por plataforma.
        meta["plataforma"] = "notas" if not meta["htb_url"] else "htb"

    return meta


# --------------------------------------------------------------------------
# Render en linea
# --------------------------------------------------------------------------
def inline(node):
    # Los comentarios HTML se filtran como texto si no los sacamos explicito:
    # en este sitio hay comentarios con URLs sueltas que ensucian el corpus.
    if isinstance(node, (Comment, Doctype)):
        return ""
    if isinstance(node, NavigableString):
        return re.sub(r"[ \t\n]+", " ", str(node))
    if not isinstance(node, Tag):
        return ""

    name = node.name
    if name in ("script", "style"):
        return ""
    if name == "code":
        txt = node.get_text().strip("\n")
        return f"`{txt}`" if txt.strip() else ""
    if name in ("strong", "b"):
        return f"**{inner(node)}**"
    if name in ("em", "i"):
        return f"*{inner(node)}*"
    if name == "br":
        return "  \n"
    if name == "del" or name == "s":
        return f"~~{inner(node)}~~"
    if name == "img":
        return img_md(node)
    if name == "a":
        href = node.get("href", "")
        txt = inner(node).strip()
        if not txt:
            return img_md(node) if node.find("img") else ""
        if not href or href.startswith("#"):
            return txt
        if not href.startswith(("http://", "https://", "mailto:")):
            href = SITE + ("" if href.startswith("/") else "/") + href
        return f"[{txt}]({href})"
    return inner(node)


def img_md(node):
    src = node.get("src") or node.get("data-src") or ""
    if not src:
        return ""
    alt = re.sub(r"\s+", " ", node.get("alt", "") or "imagen").strip()
    if not src.startswith(("http://", "https://")):
        src = SITE + ("" if src.startswith("/") else "/") + src
    return f"\n![{alt}]({src})\n"


def inner(node):
    return "".join(inline(c) for c in node.children)


# --------------------------------------------------------------------------
# Render de bloque
# --------------------------------------------------------------------------
def render_table(tbl):
    rows = []
    for tr in tbl.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        rows.append([re.sub(r"\s+", " ", inner(c)).strip().replace("|", "\\|") for c in cells])
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    out = ["| " + " | ".join(rows[0] + [""] * (width - len(rows[0]))) + " |",
           "|" + "---|" * width]
    for r in rows[1:]:
        out.append("| " + " | ".join(r + [""] * (width - len(r))) + " |")
    return "\n".join(out)


def render_list(node, depth=0, ordered=False):
    lines, idx = [], 1
    for li in node.find_all("li", recursive=False):
        subs = li.find_all(["ul", "ol"], recursive=False)
        for s in subs:
            s.extract()
        txt = re.sub(r"\s+", " ", inner(li)).strip()
        lines.append("  " * depth + f"{idx if ordered else '-'}" + (". " if ordered else " ") + txt)
        for s in subs:
            lines.append(render_list(s, depth + 1, s.name == "ol"))
        idx += 1
    return "\n".join(l for l in lines if l.strip())


def code_block_text(node):
    pre = node.find("pre") if node.name == "div" else node
    if pre is None:
        return None
    return pre.get_text().strip("\n")


def lang_of(node):
    for target in [node] + list(node.parents)[:3]:
        if not isinstance(target, Tag):
            continue
        for cls in target.get("class", []) or []:
            m = re.fullmatch(r"language-([A-Za-z0-9+#_.-]+)", cls)
            if m:
                return m.group(1)
    return ""


def render_block(node, out, skip_cover=True):
    if isinstance(node, (Comment, Doctype)):
        return
    if isinstance(node, NavigableString):
        txt = re.sub(r"\s+", " ", str(node)).strip()
        if txt:
            out.append(txt)
        return
    if not isinstance(node, Tag):
        return

    name = node.name
    if name in ("script", "style", "nav"):
        return

    # Ruido: el encabezado "Box Info" y la URL suelta de la app.
    # Los metadatos ya van en el frontmatter, asi que no van en el cuerpo.
    # Va ARRIBA de los handlers de h2/p, que si no lo consumen antes.
    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        if inner(node).strip().lower() == "box info":
            return
    if name == "p":
        if re.fullmatch(r"https://app\.hackthebox\.com/machines/\d+", inner(node).strip()):
            return

    # Cover image: ruido, la salteamos
    if name == "picture":
        img = node.find("img")
        if img and "cover-image" in (img.get("class") or []):
            return
        if img:
            out.append(img_md(img).strip())
        return

    if name == "img":
        if "cover-image" in (node.get("class") or []):
            return
        md = img_md(node).strip()
        if md:
            out.append(md)
        return

    # Tarjeta de metadatos: ya va en el frontmatter, no en el cuerpo
    if name == "div" and "htb-card" in (node.get("class") or []):
        return

    # Bloques de codigo Rouge
    if name == "div" and "highlighter-rouge" in (node.get("class") or []):
        code = code_block_text(node)
        if code is not None:
            out.append(f"```{lang_of(node)}\n{code}\n```")
        return

    if name == "pre":
        code = code_block_text(node)
        if code is not None:
            out.append(f"```{lang_of(node)}\n{code}\n```")
        return

    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(name[1])
        txt = re.sub(r"\s+", " ", inner(node)).strip()
        if txt:
            out.append("#" * level + " " + txt)
        return

    if name == "p":
        txt = inner(node).strip()
        txt = re.sub(r"\n{3,}", "\n\n", txt)
        if txt:
            out.append(txt)
        return

    if name in ("ul", "ol"):
        txt = render_list(node, 0, name == "ol")
        if txt:
            out.append(txt)
        return

    if name == "blockquote":
        lines = [l for l in inner(node).strip().split("\n") if l.strip()]
        if lines:
            out.append("\n".join("> " + l for l in lines))
        return

    if name == "table":
        txt = render_table(node)
        if txt:
            out.append(txt)
        return

    if name == "hr":
        out.append("---")
        return

    if name == "figure":
        img = node.find("img")
        if img:
            out.append(img_md(img).strip())
        cap = node.find("figcaption")
        if cap:
            c = re.sub(r"\s+", " ", inner(cap)).strip()
            if c:
                out.append(f"*{c}*")
        return

    for child in node.children:
        render_block(child, out)


def convert(html, url=""):
    soup = BeautifulSoup(html, "lxml")
    meta = extract_metadata(soup, url)

    body = (soup.select_one("div#postBody")
            or soup.select_one("div.post-content")
            or soup.select_one("article")
            or soup)

    out = []
    for child in body.children:
        render_block(child, out)

    text = "\n\n".join(o for o in out if o and o.strip())
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return meta, text.strip()


def frontmatter(meta):
    def q(v):
        return json.dumps(v, ensure_ascii=False)
    lines = ["---"]
    keys = ["maquina", "dificultad", "os", "plataforma", "release", "retire",
            "creadores", "htb_url", "app_url", "url",
            # Campos que agrega raspar.py. Booleans van SIN comillas para que
            # Obsidian los trate como propiedad booleana y no como texto.
            "tipo", "en_lista_oscp", "oscp_seccion"]
    for key in keys:
        v = meta.get(key, "")
        if key == "en_lista_oscp":
            lines.append(f"{key}: {'true' if v else 'false'}")
        else:
            lines.append(f"{key}: {q(v)}")
    lines.append("---")
    return "\n".join(lines)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    outfile = None
    if "-o" in sys.argv:
        outfile = sys.argv[sys.argv.index("-o") + 1]
    src = args[0] if args else "/tmp/t.html"
    html = open(src, encoding="utf-8", errors="replace").read()
    meta, body = convert(html)
    result = frontmatter(meta) + "\n\n" + body + "\n"
    if outfile:
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"escrito {outfile}: {len(result)} bytes", file=sys.stderr)
    else:
        print(result)
