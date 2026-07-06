#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워크시트 자동 배포 빌더.

lessons/ 아래의 각 폴더를 스캔해서, 폴더 안의 워크시트 HTML(= index.html 이외의 *.html)마다
  1) 개별 QR 코드(qr/<이름>.svg) 를 생성하고
  2) 그 폴더의 QR 모음 안내페이지(index.html) 를 자동으로 만든다.

새 워크시트를 배포하려면: lessons/ 아래 원하는 경로에 HTML 파일을 넣고 push 하면 끝.
(GitHub Actions 가 이 스크립트를 돌려 QR·안내페이지를 만들고 Pages 로 배포한다.)

폴더별로 _meta.json 을 두면 제목/배지/순서/설명/색을 지정할 수 있다(선택). 예:
{
  "title": "시대별 음악문화 조사",
  "badge": "5학년 음악 · 음악문화 탐구",
  "lead": "모둠별로 QR 을 스캔해 워크시트를 열고 내용을 채우세요.",
  "items": [
    {"file": "samguk.html", "name": "삼국시대", "sub": "고구려·백제·신라", "color": "#E53935"}
  ]
}
meta 가 없거나 일부만 있으면 HTML 에서 자동 추출한다(제목=period-name/title, 색=.ws-header 배경색).
"""
import os, re, json, html, urllib.parse
import qrcode, qrcode.image.svg

# GitHub 사용자 사이트 루트. 환경변수로 덮어쓸 수 있음(다른 저장소에서 재사용 시).
SITE_ORIGIN = os.environ.get("SITE_ORIGIN", "https://nuno4623.github.io").rstrip("/")
ROOT = os.environ.get("SITE_ROOT", ".")
LESSONS_DIR = os.path.join(ROOT, "lessons")

# 색이 지정되지 않은 워크시트에 순서대로 배정할 기본 팔레트.
PALETTE = ["#E53935", "#6D4C41", "#2E7D32", "#1565C0", "#6A1B9A", "#00838F",
           "#EF6C00", "#00695C", "#AD1457", "#283593"]


def lighten(hex_color, keep=0.12):
    """색을 흰색과 섞어 아주 옅은 배경 틴트를 만든다(keep=원색 비율)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = round(r * keep + 255 * (1 - keep))
    g = round(g * keep + 255 * (1 - keep))
    b = round(b * keep + 255 * (1 - keep))
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_title(src, stem):
    m = re.search(r'class="period-name"[^>]*>(.*?)<', src, re.S)
    if m and m.group(1).strip():
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r'class="main-title"[^>]*>(.*?)</div>', src, re.S)
    if m:
        t = re.sub(r"<br\s*/?>", " ", m.group(1))
        t = re.sub(r"<[^>]+>", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            return t
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return stem


def extract_color(src):
    m = re.search(r"\.ws-header\s*\{[^}]*?background:\s*(#[0-9A-Fa-f]{3,6})", src, re.S)
    if m:
        return m.group(1)
    m = re.search(r"--c\s*:\s*(#[0-9A-Fa-f]{3,6})", src)
    if m:
        return m.group(1)
    return None


def make_qr_svg(url, color):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    s = img.to_string().decode("utf-8")
    s = re.sub(r"<\?xml[^>]*\?>\s*", "", s)
    # path fill 을 시대색으로 (프레젠테이션 속성이라 CSS 없이도 색 지정)
    s = re.sub(r"(<path )", rf'\1fill="{color}" ', s, count=1)
    return s


def rel_url(root, filepath):
    rel = os.path.relpath(filepath, root)
    parts = rel.split(os.sep)
    return SITE_ORIGIN + "/" + "/".join(urllib.parse.quote(p) for p in parts)


def build_folder(folder):
    files = [f for f in os.listdir(folder)
             if f.lower().endswith(".html") and f.lower() != "index.html"]
    if not files:
        return None

    meta = {}
    meta_path = os.path.join(folder, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as fh:
            meta = json.load(fh)

    # 순서/메타: items 가 있으면 그 순서, 없으면 파일명 정렬
    ordered = meta.get("items")
    if ordered:
        names = {it["file"]: it for it in ordered}
        files = [it["file"] for it in ordered if it["file"] in files] + \
                [f for f in sorted(files) if f not in names]
    else:
        files = sorted(files)
        names = {}

    qr_dir = os.path.join(folder, "qr")
    os.makedirs(qr_dir, exist_ok=True)

    cards = []
    for i, fname in enumerate(files, 1):
        fpath = os.path.join(folder, fname)
        with open(fpath, encoding="utf-8") as fh:
            src = fh.read()
        stem = os.path.splitext(fname)[0]
        it = names.get(fname, {})
        title = it.get("name") or extract_title(src, stem)
        sub = it.get("sub", "")
        color = it.get("color") or extract_color(src) or PALETTE[(i - 1) % len(PALETTE)]
        light = it.get("light") or lighten(color)
        url = rel_url(ROOT, fpath)

        svg = make_qr_svg(url, color)
        with open(os.path.join(qr_dir, stem + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        embed = svg.replace("<svg ", '<svg class="qr-svg" ', 1)
        cards.append(dict(i=i, fname=fname, title=title, sub=sub,
                          color=color, light=light, url=url, svg=embed))

    badge = meta.get("badge", "")
    title = meta.get("title", os.path.basename(folder.rstrip("/")))
    lead = meta.get("lead",
                    "아래 QR 코드를 스캔해서 워크시트를 열고, 내용을 채운 뒤 저장하세요.")
    write_index(folder, badge, title, lead, cards)
    return {"title": title, "badge": badge, "count": len(cards),
            "href": os.path.relpath(os.path.join(folder, "index.html"), ROOT),
            "color": cards[0]["color"] if cards else "#1565C0"}


def write_index(folder, badge, title, lead, cards):
    esc = html.escape
    card_html = []
    for c in cards:
        card_html.append(f'''    <a class="card" href="{esc(c["fname"])}" style="--c:{c["color"]};--l:{c["light"]};">
      <div class="card-head">
        <span class="num">{c["i"]}</span>
        <div class="titles"><span class="era">{esc(c["title"])}</span>{f'<span class="sub">{esc(c["sub"])}</span>' if c["sub"] else ''}</div>
      </div>
      <div class="qr">{c["svg"]}</div>
      <div class="scan">📱 스캔하면 열려요</div>
    </a>''')
    cards_joined = "\n".join(card_html)
    badge_html = f'<span class="badge">{esc(badge)}</span>' if badge else ""
    page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} · QR 모음</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  :root {{ --bg:#F0F4F8; --fg:#22303A; --muted:#7A8A93; --card:#fff; }}
  body {{ font-family:'Noto Sans KR','Apple SD Gothic Neo',sans-serif; background:var(--bg); color:var(--fg); padding:28px 16px 60px; min-height:100vh; }}
  .wrap {{ max-width:960px; margin:0 auto; }}
  header {{ text-align:center; margin-bottom:8px; }}
  .badge {{ display:inline-block; background:#22303A; color:#fff; font-size:12px; font-weight:700; letter-spacing:.1em; padding:5px 14px; border-radius:99px; margin-bottom:14px; }}
  h1 {{ font-size:30px; font-weight:900; line-height:1.2; }}
  .lead {{ color:var(--muted); font-size:15px; margin-top:8px; line-height:1.6; }}
  .toolbar {{ text-align:center; margin:20px 0 26px; }}
  .print-btn {{ background:#22303A; color:#fff; border:none; border-radius:10px; padding:10px 22px; font-size:14px; font-weight:700; cursor:pointer; font-family:inherit; }}
  .print-btn:hover {{ opacity:.88; }}
  .grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }}
  .card {{ background:var(--card); border-radius:18px; padding:18px 16px 14px; text-decoration:none; color:inherit; box-shadow:0 4px 18px rgba(0,0,0,.08); border-top:6px solid var(--c); display:flex; flex-direction:column; align-items:center; gap:12px; transition:transform .15s, box-shadow .15s; }}
  .card:hover {{ transform:translateY(-3px); box-shadow:0 8px 26px rgba(0,0,0,.14); }}
  .card-head {{ display:flex; align-items:center; gap:10px; width:100%; }}
  .num {{ width:26px; height:26px; border-radius:50%; background:var(--c); color:#fff; font-size:13px; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
  .titles {{ display:flex; flex-direction:column; line-height:1.25; }}
  .era {{ font-size:17px; font-weight:900; color:var(--c); }}
  .sub {{ font-size:11.5px; color:var(--muted); }}
  .qr {{ width:100%; aspect-ratio:1/1; background:var(--l); border-radius:12px; padding:12px; display:flex; align-items:center; justify-content:center; }}
  .qr-svg {{ width:100%; height:100%; display:block; }}
  .qr-svg path {{ fill:var(--c); }}
  .scan {{ font-size:12px; color:var(--muted); font-weight:600; }}
  footer {{ text-align:center; color:var(--muted); font-size:12.5px; margin-top:34px; line-height:1.7; }}
  @media (max-width:720px) {{ .grid {{ grid-template-columns:repeat(2,1fr); }} h1 {{ font-size:24px; }} }}
  @media (max-width:460px) {{ .grid {{ grid-template-columns:1fr; }} }}
  @media print {{ body {{ background:#fff; padding:0; }} .toolbar {{ display:none; }} .card {{ box-shadow:none; border:1px solid #ddd; break-inside:avoid; }} .card:hover {{ transform:none; }} .grid {{ grid-template-columns:repeat(3,1fr); gap:10px; }} }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      {badge_html}
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(lead)}</p>
    </header>
    <div class="toolbar"><button class="print-btn" onclick="window.print()">🖨 QR 인쇄하기</button></div>
    <div class="grid">
{cards_joined}
    </div>
    <footer>QR 을 스마트폰·태블릿 카메라로 스캔하세요 · 자동 생성됨</footer>
  </div>
</body>
</html>
'''
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)


def write_root_landing(folders):
    esc = html.escape
    cards = []
    for f in folders:
        badge = f'<span class="lbadge">{esc(f["badge"])}</span>' if f["badge"] else ""
        cards.append(f'''    <a class="lcard" href="{esc(f["href"])}" style="--c:{f["color"]}">
      {badge}
      <span class="ltitle">{esc(f["title"])}</span>
      <span class="lmeta">워크시트 {f["count"]}개 · QR 모음 →</span>
    </a>''')
    body = "\n".join(cards) or '<p style="color:#7A8A93">아직 워크시트가 없습니다.</p>'
    page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>수업자료</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Noto Sans KR','Apple SD Gothic Neo',sans-serif; background:#F0F4F8; color:#22303A; padding:40px 16px 60px; min-height:100vh; }}
  .wrap {{ max-width:760px; margin:0 auto; }}
  h1 {{ font-size:30px; font-weight:900; text-align:center; }}
  .sub {{ text-align:center; color:#7A8A93; margin:8px 0 30px; font-size:15px; }}
  .grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }}
  .lcard {{ display:flex; flex-direction:column; gap:6px; background:#fff; border-radius:16px; padding:20px; text-decoration:none; color:inherit; box-shadow:0 4px 18px rgba(0,0,0,.08); border-left:6px solid var(--c); transition:transform .15s, box-shadow .15s; }}
  .lcard:hover {{ transform:translateY(-3px); box-shadow:0 8px 26px rgba(0,0,0,.14); }}
  .lbadge {{ font-size:11px; font-weight:700; color:var(--c); letter-spacing:.06em; }}
  .ltitle {{ font-size:19px; font-weight:900; }}
  .lmeta {{ font-size:12.5px; color:#7A8A93; }}
  @media (max-width:520px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>수업자료</h1>
    <p class="sub">아래에서 주제를 선택하세요 · 각 주제마다 QR 모음이 있습니다</p>
    <div class="grid">
{body}
    </div>
  </div>
</body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)


def main():
    if not os.path.isdir(LESSONS_DIR):
        print("lessons/ 폴더가 없습니다. 건너뜀.")
        return
    folders, total = [], 0
    for cur, dirs, _ in sorted(os.walk(LESSONS_DIR)):
        if os.path.basename(cur) == "qr":
            dirs[:] = []
            continue
        info = build_folder(cur)
        if info:
            rel = os.path.relpath(cur, ROOT)
            print(f"  ✓ {rel}  → 워크시트 {info['count']}개, QR {info['count']}개, 안내페이지 1개")
            folders.append(info)
            total += info["count"]
    write_root_landing(folders)
    print(f"완료: 폴더 {len(folders)}개 · 워크시트 {total}개 · 루트 index.html 생성")


if __name__ == "__main__":
    main()
