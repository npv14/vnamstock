"""Gắn logo doanh nghiệp vào báo cáo HTML: ảnh trước tên công ty trong <h1> và biểu tượng tab (favicon).

Run: python <SKILLS>/vnamstock/scripts/add_logo.py <file.html> [file2.html ...] --ticker KDH [--market vn|us] [--website https://...]
- Mã Việt Nam (mặc định): logo từ CDN Simplize https://cdn.simplize.vn/simplizevn/logo/<MA>.jpeg.
- Mã Mỹ: biểu tượng trang web công ty qua dịch vụ favicon Google (cần --website, hoặc tự đọc info.json Yahoo mới nhất ở <ROOT>/<MA>).
- Lưu đệm cạnh báo cáo: <thư mục báo cáo>/logo.png (thay file này bằng logo khác nếu muốn rồi chạy lại).
- Nhúng base64 nên mở offline vẫn hiện. Chạy lại nhiều lần an toàn (thay logo cũ). Không lấy được logo -> giữ nguyên file, báo ra màn hình.
"""
import argparse, base64, io, json, os, re, sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

UA = {'User-Agent': 'Mozilla/5.0'}
IMG_STYLE = ('height:40px;width:auto;max-width:170px;object-fit:contain;vertical-align:middle;'
             'margin-right:12px;border-radius:8px;background:#fff;padding:4px 6px')


def fetch(url):
    try:
        with urlopen(Request(url, headers=UA), timeout=15) as r:
            if r.status != 200 or not (r.headers.get('Content-Type') or '').startswith('image/'): return None
            b = r.read()
            return b if len(b) > 200 else None
    except Exception:
        return None


def us_website(ticker):
    runs = sorted(Path(os.environ.get('VNAMSTOCK_ROOT', '.'), ticker, 'Yahoo').glob('*_v*/raw/info.json'))
    if not runs: return None
    try: return json.loads(runs[-1].read_text(encoding='utf-8')).get('website')
    except Exception: return None


def source_bytes(ticker, market, website):
    if market == 'vn':
        return fetch(f'https://cdn.simplize.vn/simplizevn/logo/{ticker}.jpeg')
    website = website or us_website(ticker)
    if not website: return None
    dom = urlparse(website if '//' in website else '//' + website).netloc
    return fetch(f'https://www.google.com/s2/favicons?domain={dom}&sz=128') if dom else None


def mime(b):
    if b[:8] == b'\x89PNG\r\n\x1a\n': return 'image/png'
    if b[:2] == b'\xff\xd8': return 'image/jpeg'
    if b[:4] == b'\x00\x00\x01\x00': return 'image/x-icon'
    return 'image/png'


def make_variants(raw):
    """(ảnh tiêu đề cao 80px, favicon vuông 64px) dạng PNG; không có Pillow thì dùng ảnh gốc cho cả hai."""
    try:
        from PIL import Image
    except ImportError:
        return raw, raw
    im = Image.open(io.BytesIO(raw)).convert('RGBA')
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    h = 80; w = max(1, round(im.width * h / im.height))
    if w > 340: w = 340; h = max(1, round(im.height * w / im.width))
    head = im.resize((w, h), Image.LANCZOS)
    s = 64; k = min(s / im.width, s / im.height) * 0.92
    ico = Image.new('RGBA', (s, s), (255, 255, 255, 255))
    small = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    ico.alpha_composite(small, ((s - small.width) // 2, (s - small.height) // 2))
    out = []
    for x in (head, ico):
        buf = io.BytesIO(); x.save(buf, 'PNG', optimize=True); out.append(buf.getvalue())
    return out[0], out[1]


def uri(b): return f'data:{mime(b)};base64,' + base64.b64encode(b).decode('ascii')


def inject(html, head_uri, icon_uri):
    html = re.sub(r'<link rel="icon"[^>]*>', '', html)
    html = re.sub(r'<img class="co-logo"[^>]*>', '', html)
    link = f'<link rel="icon" href="{icon_uri}">'
    html = html.replace('</head>', link + '</head>', 1) if '</head>' in html else link + html
    img = f'<img class="co-logo" src="{head_uri}" alt="" style="{IMG_STYLE}">'
    return re.sub(r'(<h1\b[^>]*>)', r'\1' + img.replace('\\', r'\\'), html, count=1)


def add_logo(files, ticker, market='vn', website=None, cache=None):
    ticker = ticker.upper().strip()
    files = [Path(f) for f in files]
    cache = Path(cache) if cache else files[0].parent / 'logo.png'
    if cache.exists():
        raw = cache.read_bytes()
    else:
        raw = source_bytes(ticker, market, website)
        if not raw:
            print(f'add_logo: không lấy được logo {ticker} ({market}); giữ nguyên báo cáo'); return False
        cache.write_bytes(raw)
    head, ico = make_variants(raw)
    hu, iu = uri(head), uri(ico)
    for f in files:
        f.write_text(inject(f.read_text(encoding='utf-8'), hu, iu), encoding='utf-8')
        print(f'add_logo: {f} ({ticker})')
    return True


def main():
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+'); ap.add_argument('--ticker', required=True)
    ap.add_argument('--market', choices=['vn', 'us'], default='vn'); ap.add_argument('--website'); ap.add_argument('--cache')
    a = ap.parse_args()
    add_logo(a.files, a.ticker, a.market, a.website, a.cache)


if __name__ == '__main__':
    main()
