#!/usr/bin/env python3
"""Generate editor-style and terminal-style PNG screenshots for the report.

Renders self-contained HTML (dark VS Code-like editor chrome, and a
macOS-like terminal chrome) using headless Chrome so nothing touches
the real screen.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = Path(__file__).parent

EDITOR_CSS = """
* { box-sizing: border-box; }
body { margin:0; background:#0d1117; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
.window { width: 980px; margin: 24px auto; border-radius: 10px; overflow:hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5); background:#1e1e1e; border:1px solid #2b2b2b;}
.titlebar { background:#323233; height:38px; display:flex; align-items:center; padding:0 14px; }
.dots { display:flex; gap:8px; }
.dot { width:12px; height:12px; border-radius:50%; }
.dot.red{background:#ff5f56;} .dot.yellow{background:#ffbd2e;} .dot.green{background:#27c93f;}
.tabbar { background:#252526; display:flex; }
.tab { padding:8px 18px; font-size:13px; color:#d4d4d4; background:#1e1e1e; border-right:1px solid #2b2b2b;
  font-family:'SF Mono',Menlo,Consolas,monospace; }
.tab .dim { color:#858585; margin-left:8px; }
pre.code { margin:0; padding:16px 0 20px 0; font-family:'SF Mono',Menlo,Consolas,monospace;
  font-size:14px; line-height:1.55; overflow-x:auto; }
.line { display:flex; }
.ln { width:44px; text-align:right; padding-right:16px; color:#5a5a5a; user-select:none; flex-shrink:0; }
.code-text { white-space:pre; color:#d4d4d4; }
.kw{color:#c586c0;} .type{color:#4ec9b0;} .str{color:#ce9178;} .com{color:#6a9955;font-style:italic;}
.num{color:#b5cea8;} .fn{color:#dcdcaa;} .pp{color:#9b9b9b;} .op{color:#d4d4d4;}
.sym{color:#569cd6;}
"""

TERM_CSS = """
* { box-sizing: border-box; }
body { margin:0; background:#0d1117; font-family:-apple-system,sans-serif; }
.window { width: 900px; margin: 24px auto; border-radius: 10px; overflow:hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5); background:#1a1b26; border:1px solid #2b2b2b;}
.titlebar { background:#2c2d3a; height:34px; display:flex; align-items:center; padding:0 14px; position:relative;}
.dots { display:flex; gap:8px; }
.dot { width:12px; height:12px; border-radius:50%; }
.dot.red{background:#ff5f56;} .dot.yellow{background:#ffbd2e;} .dot.green{background:#27c93f;}
.termtitle { position:absolute; left:0; right:0; text-align:center; font-size:12px; color:#9aa0b0;
  font-family:'SF Mono',Menlo,Consolas,monospace; }
pre.term { margin:0; padding:18px 20px 24px 20px; font-family:'SF Mono',Menlo,Consolas,monospace;
  font-size:13.5px; line-height:1.5; color:#c9d1d9; white-space:pre-wrap; }
.prompt { color:#7ee787; }
.path { color:#79c0ff; }
.dollar { color:#c9d1d9; }
.cmdtext { color:#e6edf3; }
.hdr { color:#58a6ff; font-weight:bold; }
.tag-std { color:#79c0ff; }
.tag-prem { color:#d2a8ff; }
.tag-shared { color:#7ee787; }
.dim { color:#8b949e; }
.money { color:#f2cc60; }
"""

def esc(s):
    return html.escape(s)

CPP_KEYWORDS = {"class","public","private","protected","virtual","override","const",
    "static","constexpr","return","include","using","namespace","struct","void","int",
    "double","bool","true","false","auto","for","while","if","else","new","this","nullptr"}
CPP_TYPES = {"std","string","vector","shared_ptr","cout","endl","fixed","setprecision",
    "make_shared","Ride","StandardRide","PremiumRide","SharedRide","Driver","Rider"}

# Tokenizer: comment | string | word | number | other-char (kept as-is)
_CPP_TOKEN_RE = re.compile(r'//.*|"[^"]*"|\b\w+\b|\S|\s')

def highlight_cpp_line(line):
    out = []
    for tok in _CPP_TOKEN_RE.findall(line):
        if tok.startswith("//"):
            out.append(f'<span class="com">{esc(tok)}</span>')
        elif tok.startswith('"'):
            out.append(f'<span class="str">{esc(tok)}</span>')
        elif tok in CPP_KEYWORDS:
            out.append(f'<span class="kw">{esc(tok)}</span>')
        elif tok in CPP_TYPES:
            out.append(f'<span class="type">{esc(tok)}</span>')
        elif re.fullmatch(r'\d+\.?\d*', tok):
            out.append(f'<span class="num">{esc(tok)}</span>')
        else:
            out.append(esc(tok))
    return "".join(out)

ST_KEYWORDS = {"subclass","instanceVariableNames","classVariableNames","poolDictionaries",
    "category","extend","self","super","new","showCr","show","do","rounded","printString",
    "printPaddedWith","to","raisedTo"}

_ST_TOKEN_RE = re.compile(r"'[^']*'|#\w+|\b\w+\b|\S|\s")

def highlight_st_line(line):
    stripped = line.strip()
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) > 1:
        return f'<span class="com">{esc(line)}</span>'
    out = []
    for tok in _ST_TOKEN_RE.findall(line):
        if tok.startswith("'"):
            out.append(f'<span class="str">{esc(tok)}</span>')
        elif tok.startswith("#") and len(tok) > 1:
            out.append(f'<span class="type">{esc(tok)}</span>')
        elif tok in ST_KEYWORDS:
            out.append(f'<span class="kw">{esc(tok)}</span>')
        elif re.fullmatch(r'\d+\.?\d*', tok):
            out.append(f'<span class="num">{esc(tok)}</span>')
        else:
            out.append(esc(tok))
    return "".join(out)

def render_editor(title, tab, lines, start_line, highlighter, out_html, out_png, width=1020, height=None):
    body_lines = []
    for i, line in enumerate(lines):
        ln = start_line + i
        code_html = highlighter(line) if line.strip() else ""
        body_lines.append(f'<div class="line"><span class="ln">{ln}</span><span class="code-text">{code_html}</span></div>')
    body = "\n".join(body_lines)
    html_doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{EDITOR_CSS}</style></head>
<body>
<div class="window">
  <div class="titlebar"><div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div></div>
  <div class="tabbar"><div class="tab">{esc(tab)}</div></div>
  <pre class="code">{body}</pre>
</div>
</body></html>"""
    Path(out_html).write_text(html_doc)
    h = height or (80 + 24 * len(lines) + 60)
    run_chrome(out_html, out_png, width, h)

def render_terminal(title, prompt_lines, out_html, out_png, width=940, height=None):
    body = "\n".join(prompt_lines)
    html_doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{TERM_CSS}</style></head>
<body>
<div class="window">
  <div class="titlebar"><div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
    <div class="termtitle">{esc(title)}</div></div>
  <pre class="term">{body}</pre>
</div>
</body></html>"""
    Path(out_html).write_text(html_doc)
    h = height or 700
    run_chrome(out_html, out_png, width, h)

def run_chrome(html_path, png_path, width, height):
    # Render with generous extra height (line-height math is unreliable to
    # predict exactly), then autocrop the PNG down to actual content bounds.
    tall = height + 800
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        f"--screenshot={png_path}", f"--window-size={width},{tall}",
        "--force-device-scale-factor=2",
        f"file://{Path(html_path).resolve()}"
    ], check=True, capture_output=True)
    autocrop(png_path)
    print(f"wrote {png_path}")

def autocrop(png_path, pad=20, tolerance=12):
    from PIL import Image
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    bg = im.getpixel((2, 2))
    px = im.load()

    def differs(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > tolerance

    last_row = 0
    for y in range(h - 1, -1, -1):
        row_has_content = False
        for x in range(0, w, 4):
            if differs(px[x, y]):
                row_has_content = True
                break
        if row_has_content:
            last_row = y
            break
    crop_h = min(h, last_row + pad)
    im.crop((0, 0, w, crop_h)).save(png_path)

def colorize_output_line(line):
    e = esc(line)
    if line.startswith("====="):
        return f'<span class="dim">{e}</span>'
    if "RIDE SHARING SYSTEM" in line:
        return f'<span class="hdr">{e}</span>'
    if line.startswith("---"):
        return f'<span class="hdr">{e}</span>'
    e = re.sub(r'\$([0-9]+\.[0-9]{2})', r'<span class="money">$\1</span>', e)
    e = e.replace("[Standard]", '<span class="tag-std">[Standard]</span>')
    e = e.replace("[Premium] ", '<span class="tag-prem">[Premium] </span>')
    e = e.replace("[Shared]  ", '<span class="tag-shared">[Shared]  </span>')
    return e

if __name__ == "__main__":
    action = sys.argv[1]

    if action == "cpp_code":
        src = Path.home() / "projects/ride-sharing-oop/cpp/RideSharingSystem.cpp"
        all_lines = src.read_text().splitlines()
        snippet = all_lines[9:96]  # Ride, StandardRide, PremiumRide classes
        render_editor("C++", "RideSharingSystem.cpp", snippet, 10, highlight_cpp_line,
                      "/tmp/cpp_code.html", str(HERE / "cpp_code.png"))

    elif action == "cpp_output":
        text = (Path("/tmp/cpp_output.txt")).read_text().splitlines()
        colored = [colorize_output_line(l) for l in text]
        prompt = ['<span class="prompt">➜</span>  <span class="path">~/projects/ride-sharing-oop/cpp</span> <span class="dollar">$</span> <span class="cmdtext">./RideSharingSystem</span>', ""]
        render_terminal("cpp — ./RideSharingSystem", prompt + colored,
                        "/tmp/cpp_output.html", str(HERE / "cpp_output.png"), height=560)

    elif action == "st_code":
        src = Path.home() / "projects/ride-sharing-oop/smalltalk/RideSharingSystem.st"
        all_lines = src.read_text().splitlines()
        snippet = all_lines[24:] # from Ride extend through PremiumRide
        # trim to Ride..PremiumRide block only
        text = src.read_text()
        idx_start = text.index("Ride extend [")
        idx_end = text.index("SharedRide: a third ride type")
        snippet_text = text[idx_start:idx_end].rstrip()
        snippet = snippet_text.splitlines()
        start_no = text[:idx_start].count("\n") + 1
        render_editor("Smalltalk", "RideSharingSystem.st", snippet, start_no, highlight_st_line,
                      "/tmp/st_code.html", str(HERE / "st_code.png"))

    elif action == "st_output":
        text = (Path("/tmp/st_output.txt")).read_text().splitlines()
        colored = [colorize_output_line(l) for l in text]
        prompt = ['<span class="prompt">➜</span>  <span class="path">~/projects/ride-sharing-oop/smalltalk</span> <span class="dollar">$</span> <span class="cmdtext">gst RideSharingSystem.st</span>', ""]
        render_terminal("smalltalk — gst RideSharingSystem.st", prompt + colored,
                        "/tmp/st_output.html", str(HERE / "st_output.png"), height=560)

    elif action == "driver_code":
        src = Path.home() / "projects/ride-sharing-oop/cpp/RideSharingSystem.cpp"
        text = src.read_text()
        idx_start = text.index("class Driver")
        idx_end = text.index("class Rider")
        snippet_text = text[idx_start:idx_end].rstrip()
        snippet = snippet_text.splitlines()
        start_no = text[:idx_start].count("\n") + 1
        render_editor("C++", "RideSharingSystem.cpp — Driver (encapsulation)", snippet, start_no, highlight_cpp_line,
                      "/tmp/driver_code.html", str(HERE / "driver_code.png"))
