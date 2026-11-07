"""CAN SLIM illustrative scenario chart (SVG) for VNamStock reports.

Draws recent actual prices, an assumed base, a buy at the pivot, then three
hypothetical branches: stop-loss, take-profit, and sell on a bad signal
(close below MA50 with heavy volume). Paths are deterministic illustrations,
NOT forecasts.

Usage:
  python -I canslim_scenario_chart.py --history prices.json --symbol FPT \
      --pivot 58300 --base-low 54000 --out chart.svg [--levels levels.json]
prices.json: {"<SYMBOL>": [{"Ngay": "dd/mm/yyyy", "GiaDieuChinh": 54.0, ...}, ...]}
newest-first, as returned by CafeF PriceHistory (prices in thousand VND).
"""
import argparse, json, math

def vnd(p):
    return f'{p:,.0f}'.replace(',', '.')

HALO = 'paint-order:stroke;stroke:var(--card);stroke-width:3px;stroke-linejoin:round'

def ma(series, i, k=50):
    w = series[max(0, i - k + 1):i + 1]
    return sum(w) / len(w)

def build(hist, pivot, base_low, n_actual=120, n_base=30, stop=0.07, stop2=0.08, tp=(0.20, 0.25)):
    actual = [x['GiaDieuChinh'] * 1000 for x in reversed(hist)][-n_actual:]
    dates = [x['Ngay'] for x in reversed(hist)][-n_actual:]
    last = actual[-1]
    # base: oscillate between base_low and just under pivot, ending near pivot
    base = []
    for t in range(1, n_base + 1):
        mid = (base_low + pivot * 0.985) / 2
        amp = (pivot * 0.985 - base_low) / 2
        drift = (t / n_base) ** 2 * amp * 0.6
        base.append(mid + drift - amp * math.cos(t / n_base * 3 * math.pi) * (1 - t / n_base * 0.5) * 0.9)
    base[0] = last + (base[0] - last) * 0.3
    entry = pivot
    brk = pivot * 1.02
    def walk(start, target, n, wiggle=0.012, phase=0.0):
        out = []
        for t in range(1, n + 1):
            v = start + (target - start) * t / n
            out.append(v * (1 + wiggle * math.sin(t * 1.3 + phase)))
        out[-1] = target
        return out
    a = walk(brk, entry * (1 - stop2), 12, 0.01, 0.5)                     # stop-loss branch
    b = walk(brk, entry * (1 + tp[0] + 0.02), 35, 0.015, 1.0)             # take-profit branch
    c_up = walk(brk, entry * 1.12, 20, 0.012, 2.0)
    pre = actual + base + [brk]
    c = c_up[:]
    # decline until close < MA50 (computed on full path), then mark sell
    sell_c = None
    v = c_up[-1]
    while len(c) < 60:
        v *= 0.988
        c.append(v)
        full = pre + c
        if v < ma(full, len(full) - 1):
            sell_c = (len(full) - 1, v)
            break
    full_c = pre + c
    ma50_c = [ma(full_c, i) for i in range(len(full_c))]
    # stop / take-profit trigger points
    i0 = len(pre) - 1
    sell_a = next(((i0 + 1 + i, x) for i, x in enumerate(a) if x <= entry * (1 - stop)), (i0 + len(a), a[-1]))
    sell_b = next(((i0 + 1 + i, x) for i, x in enumerate(b) if x >= entry * (1 + tp[0])), (i0 + len(b), b[-1]))
    return dict(actual=actual, dates=dates, base=base, brk=brk, entry=entry, a=a, b=b, c=c, ma50_c=ma50_c,
                sell_a=sell_a, sell_b=sell_b, sell_c=sell_c, i_buy=i0, n_actual=len(actual), stop=stop, stop2=stop2, tp=tp)

def svg(d, symbol, pivot, W=760, H=380, pad=(58, 20, 24, 40)):
    L, R, T, B = pad
    n_tot = d['i_buy'] + 1 + max(len(d['a']), len(d['b']), len(d['c']))
    allp = d['actual'] + d['base'] + d['a'] + d['b'] + d['c'] + [d['entry'] * (1 + d['tp'][1])]
    lo, hi = min(allp) * 0.97, max(allp) * 1.02
    X = lambda i: L + (W - L - R) * i / (n_tot - 1)
    Y = lambda p: T + (H - T - B) * (1 - (p - lo) / (hi - lo))
    def path(points, style, dash=''):
        pts = ' '.join(f'{X(i):.1f},{Y(p):.1f}' for i, p in points)
        return f'<polyline points="{pts}" fill="none" style="{style}"{dash}/>'
    i_buy = d['i_buy']; n_act = d['n_actual']
    e = d['entry']; s7, s8 = e * (1 - d['stop']), e * (1 - d['stop2']); t20, t25 = e * (1 + d['tp'][0]), e * (1 + d['tp'][1])
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Minh họa kịch bản CAN SLIM {symbol}">']
    # grid & y labels
    step = 5000 if hi - lo > 25000 else (2000 if hi - lo > 8000 else 1000)
    v = math.ceil(lo / step) * step
    while v < hi:
        o.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" style="stroke:var(--line)"/>')
        o.append(f'<text x="{L-6}" y="{Y(v)+4:.1f}" text-anchor="end">{v/1000:g}k</text>')
        v += step
    # zones
    def band(p1, p2, color, label):
        o.append(f'<rect x="{X(i_buy):.1f}" y="{Y(p2):.1f}" width="{W-R-X(i_buy):.1f}" height="{Y(p1)-Y(p2):.1f}" style="fill:{color};opacity:.14"/>')
        o.append(f'<text x="{X(i_buy)-8:.1f}" y="{(Y(p1)+Y(p2))/2+4:.1f}" text-anchor="end" style="fill:{color};{HALO}">{label}</text>')
    band(e, e * 1.05, 'var(--acc)', f'Vùng mua {vnd(e)}–{vnd(e*1.05)}')
    band(s8, s7, 'var(--bad)', f'Cắt lỗ 7–8%: {vnd(s8)}–{vnd(s7)}')
    band(t20, t25, 'var(--good)', f'Chốt lời 20–25%: {vnd(t20)}–{vnd(t25)}')
    o.append(f'<line x1="{L}" y1="{Y(pivot):.1f}" x2="{W-R}" y2="{Y(pivot):.1f}" style="stroke:var(--acc);stroke-dasharray:6 4"/>')
    o.append(f'<text x="{L+4}" y="{Y(pivot)-5:.1f}" style="fill:var(--acc);{HALO}">Pivot giả định {vnd(pivot)}</text>')
    # today divider
    o.append(f'<line x1="{X(n_act-1):.1f}" y1="{T}" x2="{X(n_act-1):.1f}" y2="{H-B}" style="stroke:var(--mut);stroke-dasharray:2 4"/>')
    o.append(f'<text x="{X(n_act-1)-4:.1f}" y="{T+10}" text-anchor="end">Thực tế ← | → Giả định</text>')
    # lines
    o.append(path(list(enumerate(d['actual'])), 'stroke:var(--ink);stroke-width:1.8'))
    base_pts = [(n_act - 1, d['actual'][-1])] + [(n_act + i, p) for i, p in enumerate(d['base'])] + [(i_buy, d['brk'])]
    o.append(path(base_pts, 'stroke:var(--mut);stroke-width:1.6', ' stroke-dasharray="4 3"'))
    ma_pts = [(i, m) for i, m in enumerate(d['ma50_c']) if i >= 49]
    o.append(path(ma_pts, 'stroke:var(--warn);stroke-width:1;opacity:.7', ' stroke-dasharray="1 3"'))
    for key, color in (('b', 'var(--good)'), ('c', 'var(--warn)'), ('a', 'var(--bad)')):
        pts = [(i_buy, d['brk'])] + [(i_buy + 1 + i, p) for i, p in enumerate(d[key])]
        o.append(path(pts, f'stroke:{color};stroke-width:2'))
    # markers
    def mark(i, p, color, label, dy=-10, anchor='middle'):
        o.append(f'<circle cx="{X(i):.1f}" cy="{Y(p):.1f}" r="5" style="fill:{color};stroke:var(--card);stroke-width:1.5"/>')
        o.append(f'<text x="{X(i):.1f}" y="{Y(p)+dy:.1f}" text-anchor="{anchor}" style="fill:{color};font-weight:700;{HALO}">{label}</text>')
    o.append(f'<circle cx="{X(i_buy):.1f}" cy="{Y(d["brk"]):.1f}" r="5" style="fill:var(--acc);stroke:var(--card);stroke-width:1.5"/>')
    o.append(f'<text x="{X(i_buy)-8:.1f}" y="{Y(d["brk"])-8:.1f}" text-anchor="end" style="fill:var(--acc);font-weight:700;{HALO}">① Mua</text>')
    mark(*d['sell_a'], 'var(--bad)', '② Cắt lỗ', 20)
    o.append(f'<circle cx="{X(d["sell_b"][0]):.1f}" cy="{Y(d["sell_b"][1]):.1f}" r="5" style="fill:var(--good);stroke:var(--card);stroke-width:1.5"/>')
    o.append(f'<text x="{X(d["sell_b"][0])-9:.1f}" y="{Y(d["sell_b"][1])+4:.1f}" text-anchor="end" style="fill:var(--good);font-weight:700;{HALO}">③ Chốt lời</text>')
    if d['sell_c']:
        mark(*d['sell_c'], 'var(--warn)', '④ Tín hiệu xấu', 20)
    # x labels
    o.append(f'<text x="{X(0):.1f}" y="{H-12}">{d["dates"][0]}</text>')
    o.append(f'<text x="{X(n_act-1):.1f}" y="{H-12}" text-anchor="middle">{d["dates"][-1]}</text>')
    o.append(f'<text x="{W-R:.1f}" y="{H-12}" text-anchor="end">+{n_tot-n_act} phiên giả định</text>')
    o.append('</svg>')
    return '\n'.join(o)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--history', required=True); ap.add_argument('--symbol', required=True)
    ap.add_argument('--pivot', type=float, required=True); ap.add_argument('--base-low', type=float, required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--levels')
    ap.add_argument('--base-sessions', type=int, default=30, help='so phien nen gia gia dinh truoc khi vuot pivot (it hon neu nen that da hinh thanh)')
    a = ap.parse_args()
    hist = json.load(open(a.history, encoding='utf-8'))[a.symbol]
    d = build(hist, a.pivot, a.base_low, n_base=a.base_sessions)
    open(a.out, 'w', encoding='utf-8').write(svg(d, a.symbol, a.pivot))
    e = d['entry']
    lv = {'pivot': a.pivot, 'buy_zone': [e, e * 1.05], 'stop_7': e * 0.93, 'stop_8': e * 0.92,
          'tp_20': e * 1.20, 'tp_25': e * 1.25, 'bad_signal_sell': d['sell_c'][1] if d['sell_c'] else None,
          'bad_signal_ma50': d['ma50_c'][d['sell_c'][0]] if d['sell_c'] else None,
          'bad_signal_pct': (d['sell_c'][1] / e - 1) if d['sell_c'] else None,
          'sessions': {'stop': d['sell_a'][0] - d['i_buy'], 'take_profit': d['sell_b'][0] - d['i_buy'],
                       'bad_signal': (d['sell_c'][0] - d['i_buy']) if d['sell_c'] else None}}
    if a.levels:
        json.dump(lv, open(a.levels, 'w', encoding='utf-8'), indent=2)
    print(json.dumps(lv, indent=2))
