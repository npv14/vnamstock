"""Cập nhật khối THEME: BANG GIA trong các file HTML/CSS theo bản gốc assets/theme-bang-gia.css.
Dùng: python apply_theme.py <file hoặc thư mục>...  (chỉ đụng file đã có khối theme; chạy lại nhiều lần vẫn an toàn)"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
THEME = open(os.path.join(HERE, '..', 'assets', 'theme-bang-gia.css'), encoding='utf-8').read().strip()
PAT = re.compile(r'/\* ==== THEME: BANG GIA.*?==== END THEME ==== \*/', re.S)


def apply(path):
    s = open(path, encoding='utf-8').read()
    if not PAT.search(s):
        return False
    t = PAT.sub(lambda m: THEME, s)
    if t != s:
        open(path, 'w', encoding='utf-8', newline='').write(t)
    return t != s


n = 0
for a in sys.argv[1:]:
    files = [a] if os.path.isfile(a) else [os.path.join(r, f) for r, _, fs in os.walk(a) for f in fs if f.lower().endswith(('.html', '.css'))]
    for f in files:
        if '_theme-demo' in f.replace(os.sep, '/') or os.path.abspath(f) == os.path.abspath(os.path.join(HERE, '..', 'assets', 'theme-bang-gia.css')):
            continue
        if apply(f):
            n += 1; print('đã cập nhật:', f)
print('tổng:', n)
