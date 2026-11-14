#!/usr/bin/env python3
"""Tô màu theo dấu cho mọi số phần trăm trong báo cáo HTML (VNamStock + USStock).

Quy tắc của người dùng (11/11/2026): số % có dấu trừ đứng trước -> chữ đỏ (.neg),
có dấu cộng đứng trước -> chữ xanh (.pos). Áp cho toàn bộ chữ trong báo cáo,
không phụ thuộc việc người viết có nhớ gắn class hay không.

Dùng:
    python colorize_signs.py <file.html> [<file2.html> ...]     # sửa tại chỗ
Hoặc trong script khác:
    from colorize_signs import colorize;  html = colorize(html)

Chạy lại nhiều lần vẫn an toàn (tự gỡ lớp bọc cũ rồi bọc lại).
Không coi là số âm: khoảng "7–8%" (gạch nối dài), "20-25%" (gạch nối giữa hai số).
"""
import re
import sys

# dấu: + / - (hyphen) / − (U+2212). Phải đứng đầu "từ": không liền sau chữ, số, dấu chấm/phẩy/%.
_SIGNED = re.compile(r'(?<![\w.,%])([+\-−])(\s?\d[\d.,]*\s?%)')
_WRAP = re.compile(r'<span class="sg (?:pos|neg)">(.*?)</span>', re.S)
_TAG = re.compile(r'(<[^>]+>)')
_SKIP = ('style', 'script', 'svg', 'title', 'head', 'textarea', 'pre', 'code')


def _wrap(m):
    cls = 'pos' if m.group(1) == '+' else 'neg'
    return f'<span class="sg {cls}">{m.group(1)}{m.group(2)}</span>'


def colorize(html: str) -> str:
    html = _WRAP.sub(r'\1', html)          # gỡ lớp bọc cũ -> chạy lại không bọc chồng
    out, skip = [], []
    for part in _TAG.split(html):
        if part.startswith('<') and part.endswith('>'):
            m = re.match(r'<\s*(/?)\s*([a-zA-Z0-9]+)', part)
            if m and m.group(2).lower() in _SKIP and not part.rstrip().endswith('/>'):
                name = m.group(2).lower()
                if m.group(1):
                    if skip and skip[-1] == name:
                        skip.pop()
                else:
                    skip.append(name)
            out.append(part)
        elif skip:
            out.append(part)
        else:
            out.append(_SIGNED.sub(_wrap, part))
    return ''.join(out)


def colorize_file(path: str) -> int:
    with open(path, encoding='utf-8') as f:
        src = f.read()
    dst = colorize(src)
    if dst != src:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(dst)
    return dst.count('<span class="sg ')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        print(f'{p}: {colorize_file(p)} số % đã tô màu theo dấu')
