"""5 con số lớn + Nợ (Phil Town, Rule #1) cho báo cáo 4M VNamStock — 6 mục kiểm tra sức khỏe doanh nghiệp.

  1. ROIC và ROE            mức tốt ≥ 10% mỗi năm
  2. Tăng BVPS              mức tốt ≥ 10%/năm
  3. Tăng doanh thu         mức tốt ≥ 14%/năm
  4. Tăng EPS               mức tốt ≥ 24%/năm
  5. Tăng dòng tiền (CFO)   mức tốt ≥ 11%/năm
  6. Nợ vay                 tốt khi nợ vay ≤ 4 lần LN mẹ 4 quý gần nhất; > 4 lần là xấu, phải giải thích lý do

Ngưỡng là quy tắc của chuyên gia (ghi chú 09/11/2026), sửa được bằng tham số.
"Ổn định" (consistent): xét tăng trưởng kép 4 năm, 3 năm và 1 năm gần nhất —
  Ổn định = cả ba ≥ 10%; Dao động = có mức < 10% nhưng không âm; Không ổn định = có mức âm.
Đánh giá theo mức tốt dùng tăng trưởng kép cả kỳ: Tốt ≥ mức tốt; Khá 10% → dưới mức tốt; Yếu < 10%.

Đầu vào: five_year.json của ../../vnamstock-full-report/scripts/five_year_metrics.py (bản có cột 'roic').
Nợ vay lấy từ CafeF CDKT năm (mã 320 vay ngắn hạn + 338 vay dài hạn; 110 tiền, 120 đầu tư tài chính ngắn hạn)
và CDKT quý gần nhất. Ngân hàng/bảo hiểm: nợ là nguyên liệu kinh doanh → mục 6 ghi N/A.

Ví dụ:
  python -I big_five.py --five-year <ROOT>/FPT/BasicMetrics/2026-11-09_v01/five_year.json --out <ROOT>/FPT/4M/big_five
In JSON + đoạn HTML <section id="bigfive"> (big_five.html) để dán ngay sau mục 3a Moat — 5 loại (Moat đứng trước, số liệu đứng sau).
"""
import argparse, json, os, sys, html, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://cafef.vn/'}
API = 'https://apiweb.cafef.vn/api/v2/BCTC/GetReportCDKT'


def vn(x, d=0):
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, d=1):
    return "N/A" if x is None else vn(x * 100, d) + "%"


def fetch_cdkt(sym, kind, raw):
    out = {}
    for p in (1, 2) if kind == 'NAM' else (1,):
        url = f'{API}?symbol={sym}&pageIndex={p}&pageSize=4&reportType=ALL&TypeTime={kind}'
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30))
        json.dump(d, open(os.path.join(raw, f'cdkt_{kind}_p{p}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        for blk in d['value']['data']:
            for per in blk['data']:
                out.setdefault(per['time'], {}).update({x['code']: x['value'] for x in per['data']})
    return out


def cagr(a, b, n):
    if a is None or b is None or a <= 0 or b <= 0 or n <= 0: return None
    return (b / a) ** (1 / n) - 1


def growth(series, years):
    """series {năm: giá trị}; trả CAGR 4 năm, 3 năm, 1 năm và tăng từng năm."""
    y = [str(x) for x in years]
    last = y[-1]
    g = {'4y': cagr(series.get(y[0]), series.get(last), len(y) - 1),
         '3y': cagr(series.get(y[-4]), series.get(last), 3) if len(y) >= 4 else None,
         '1y': cagr(series.get(y[-2]), series.get(last), 1)}
    yoy = {y[i]: cagr(series.get(y[i - 1]), series.get(y[i]), 1) for i in range(1, len(y))}
    return g, yoy


def consistency(g, floor):
    vals = [v for v in g.values()]
    if any(v is None for v in vals): return 'Thiếu dữ liệu', 'p-warn'
    if any(v < 0 for v in vals): return 'Không ổn định', 'p-bad'
    if all(v >= floor for v in vals): return 'Ổn định', 'p-good'
    return 'Dao động', 'p-warn'


def grade(v, good, floor):
    if v is None: return 'Thiếu dữ liệu', 'p-warn'
    if v >= good: return 'Tốt', 'p-good'
    if v >= floor: return 'Khá', 'p-warn'
    return 'Yếu', 'p-bad'


API1 = 'https://apiweb.cafef.vn/api/v1/BCTC'


def fetch_v1(sym, rep, raw, pages=(1, 2)):
    """CafeF v1 theo quý (GetReportSummary / GetReportLCTT) → {kỳ: {mã: giá trị}}; LCTT quý là số lũy kế từ đầu năm."""
    out = {}
    for p in pages:
        url = f'{API1}/{rep}?symbol={sym}&pageIndex={p}&pageSize=4&reportType=ALL&TypeTime=QUY'
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30))
        json.dump(d, open(os.path.join(raw, f'{rep}_QUY_p{p}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        for blk in d['value']['data']:
            for per in blk['data']:
                out.setdefault(per['time'], {}).update({x['code']: x['value'] for x in per['data']})
    return out


def estimate_year(sym, rows, meta, raw, div_ps, debt_now):
    """Ước tính năm đang dở (yêu cầu 14/11/2026): số dòng chảy = tổng các quý đã công bố ÷ n × 4;
    vốn chủ cuối năm = vốn chủ quý gần nhất + LN mẹ TB 1 quý × số quý còn lại − cổ tức tiền trả trước cuối năm;
    nợ vay = số quý gần nhất. ROIC/ROE cùng công thức five_year_metrics.py."""
    years = meta['years']; last = years[-1]
    q = fetch_v1(sym, 'GetReportSummary', raw)
    keys = sorted((t for t in q if t.startswith('Q')), key=lambda t: (int(t.split('-')[1]), int(t[1])))
    if not keys: return None
    ly, n = int(keys[-1].split('-')[1]), int(keys[-1][1])
    if ly != last + 1: return None
    if n == 4:
        print(f'LƯU Ý: đã có đủ 4 quý {ly} — chạy lại five_year_metrics.py để có cột năm {ly} thật, không cần ước tính.', file=sys.stderr)
        return None
    Q = [f'Q{i}-{ly}' for i in range(1, n + 1)]; prev = f'Q4-{last}'
    if any(t not in q for t in Q + [prev]): return None
    cf = fetch_v1(sym, 'GetReportLCTT', raw, pages=(1,))
    k = 4 / n; SH = meta['shares_now']
    s = lambda c: sum(q[t].get(c) or 0 for t in Q)
    eq = lambda d: None if d.get('CDKT_31') is None else d['CDKT_31'] - (d.get('CDKT_35') or 0)
    cap = lambda d: None if d.get('CDKT_27') is None or d.get('CDKT_29') is None else d['CDKT_27'] - d['CDKT_29']
    rev_n, ln_n = s('KQKD_2'), s('KQKD_14')
    gp, sell, adm, pbt, pat = (s(c) for c in ('KQKD_4', 'KQKD_7', 'KQKD_8', 'KQKD_12', 'KQKD_13'))
    tax = 1 - pat / pbt if pbt and pbt > 0 else 0.2
    nopat = (gp - abs(sell) - abs(adm)) * (1 - min(max(tax, 0), 0.5)) * k if gp else None
    c0, c1 = cap(q[prev]), cap(q[Q[-1]])
    e0, e1 = eq(q[prev]), eq(q[Q[-1]])
    e_end = None if e1 is None else e1 + ln_n / n * (4 - n) - div_ps * SH
    ln = ln_n * k
    cfo_ytd = (cf.get(Q[-1]) or {}).get('HDKD_20')
    est = {'year': ly, 'n': n, 'quarters': Q, 'rev_n': rev_n, 'ln_n': ln_n, 'cfo_ytd': cfo_ytd, 'div_ps': div_ps,
           'roic': nopat / ((c0 + c1) / 2) if nopat and c0 and c1 else None,
           'roe': ln / ((e0 + e_end) / 2) if e0 and e_end else None,
           'doanh_thu': rev_n * k, 'ln_me': ln, 'eps_pf': ln / SH, 'bvps_pf': e_end / SH if e_end else None,
           'cfo': cfo_ytd * k if cfo_ytd is not None else None,
           'no_vay': debt_now, 'lan_ln': debt_now / ln if debt_now is not None and ln > 0 else None}
    r0 = rows[str(last)]
    est['yoy'] = {key: (est[key] / r0[key] - 1 if est.get(key) and r0.get(key) and r0[key] > 0 else None)
                  for key in ('doanh_thu', 'eps_pf', 'bvps_pf', 'cfo')}
    return est


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--five-year', required=True, help='five_year.json (có roic)')
    ap.add_argument('--out', required=True, help='thư mục lưu big_five.json/.html và raw/')
    ap.add_argument('--floor', type=float, default=10, help='mức tối thiểu %% (ROIC/ROE, ổn định)')
    ap.add_argument('--bvps-good', type=float, default=10)
    ap.add_argument('--sales-good', type=float, default=14)
    ap.add_argument('--eps-good', type=float, default=24)
    ap.add_argument('--cash-good', type=float, default=11)
    ap.add_argument('--debt-max', type=float, default=4, help='nợ vay tối đa bằng bao nhiêu lần LN mẹ 4 quý')
    ap.add_argument('--financial', action='store_true', help='ngân hàng/bảo hiểm/chứng khoán: mục nợ ghi N/A')
    ap.add_argument('--debt-reason', default='', help='lý do nợ cao (HTML được phép); bắt buộc khi nợ vượt ngưỡng')
    ap.add_argument('--no-estimate', action='store_true', help='không thêm cột năm đang dở ước tính')
    ap.add_argument('--est-dividend', type=float, default=0, help='cổ tức tiền đ/cp sẽ trả trước cuối năm (trừ khỏi vốn chủ ước tính)')
    ap.add_argument('--est-note', default='', help='giải thích cách đọc cột ước tính (HTML): mùa vụ, thay đổi hợp nhất, khoản bất thường…')
    a = ap.parse_args()
    fy = json.load(open(a.five_year, encoding='utf-8'))
    meta, rows = fy['meta'], fy['rows']
    sym, years = meta['symbol'], meta['years']
    if not any('roic' in rows[str(y)] for y in years):
        sys.exit('five_year.json chưa có cột roic: chạy lại five_year_metrics.py bản mới rồi thử lại.')
    floor = a.floor / 100
    os.makedirs(os.path.join(a.out, 'raw'), exist_ok=True)
    col = lambda k: {str(y): rows[str(y)].get(k) for y in years}

    # 1. ROIC, ROE
    roic, roe = col('roic'), col('roe')
    def ret_status(s):
        v = [x for x in s.values() if x is not None]
        if len(v) < len(years): return 'Thiếu dữ liệu', 'p-warn'
        return ('Tốt', 'p-good') if min(v) >= floor else (('Khá', 'p-warn') if sum(v) / len(v) >= floor else ('Yếu', 'p-bad'))
    m1 = {'roic': roic, 'roe': roe, 'roic_ttm': rows.get('TTM', {}).get('roic'), 'roe_ttm': rows.get('TTM', {}).get('roe'),
          'roic_status': ret_status(roic), 'roe_status': ret_status(roe)}

    # 2–5. Tăng trưởng
    specs = [('bvps', 'bvps_pf', a.bvps_good), ('sales', 'doanh_thu', a.sales_good),
             ('eps', 'eps_pf', a.eps_good), ('cash', 'cfo', a.cash_good)]
    G = {}
    for name, key, good in specs:
        g, yoy = growth(col(key), years)
        G[name] = {'key': key, 'good': good / 100, 'values': col(key), 'cagr': g, 'yoy': yoy,
                   'consistency': consistency(g, floor), 'grade': grade(g['4y'], good / 100, floor)}

    # 6. Nợ vay
    debt = None
    if not a.financial:
        yr = fetch_cdkt(sym, 'NAM', os.path.join(a.out, 'raw'))
        q = fetch_cdkt(sym, 'QUY', os.path.join(a.out, 'raw'))
        lq = sorted(q, key=lambda t: (int(t.split('-')[1]), int(t[1])))[-1]
        def pack(d):
            vay = (d.get('320') or 0) + (d.get('338') or 0)
            cash = (d.get('110') or 0) + (d.get('120') or 0)
            return {'vay_nh': d.get('320') or 0, 'vay_dh': d.get('338') or 0, 'no_vay': vay, 'tien_dtnh': cash, 'no_vay_rong': vay - cash}
        ttm_ln = rows.get('TTM', {}).get('ln_me')
        hist = {}
        for y in years:
            d = yr.get(str(y))
            if d:
                p = pack(d); ln = rows[str(y)].get('ln_me')
                p['ln_me'] = ln; p['lan_ln'] = p['no_vay'] / ln if ln and ln > 0 else None
                hist[str(y)] = p
        cur = pack(q[lq]); cur['ky'] = lq; cur['ln_me_ttm'] = ttm_ln
        cur['lan_ln'] = cur['no_vay'] / ttm_ln if ttm_ln and ttm_ln > 0 else None
        cur['lan_ln_rong'] = max(cur['no_vay_rong'], 0) / ttm_ln if ttm_ln and ttm_ln > 0 else None
        x = cur['lan_ln']
        st = ('Thiếu dữ liệu', 'p-warn') if x is None else (('Tốt', 'p-good') if x <= a.debt_max else ('Xấu', 'p-bad'))
        if st[0] == 'Xấu' and not a.debt_reason:
            print('CẢNH BÁO: nợ vay vượt ngưỡng — chạy lại với --debt-reason để giải thích lý do.', file=sys.stderr)
        debt = {'hist': hist, 'current': cur, 'max': a.debt_max, 'status': st, 'reason': a.debt_reason}

    est = None
    if not a.no_estimate:
        est = estimate_year(sym, rows, meta, os.path.join(a.out, 'raw'), a.est_dividend,
                            debt['current']['no_vay'] if debt else None)
        if est and not a.est_note:
            print('NHẮC: có cột ước tính — kiểm tra mùa vụ quý 4, thay đổi hợp nhất, khoản bất thường rồi giải thích bằng --est-note.', file=sys.stderr)

    res = {'symbol': sym, 'years': years, 'thresholds': vars(a), 'roic_roe': m1, 'growth': G, 'debt': debt, 'estimate': est}
    json.dump(res, open(os.path.join(a.out, 'big_five.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2, default=str)
    open(os.path.join(a.out, 'big_five.html'), 'w', encoding='utf-8').write(render(res, a))

    # tóm tắt ra màn hình
    print(f"{sym} {years[0]}–{years[-1]}")
    print('1 ROIC', ' | '.join(pct(roic[str(y)]) for y in years), '→', m1['roic_status'][0])
    print('  ROE ', ' | '.join(pct(roe[str(y)]) for y in years), '→', m1['roe_status'][0])
    for n, d in G.items():
        print(f"{n:5} 4y {pct(d['cagr']['4y'])} 3y {pct(d['cagr']['3y'])} 1y {pct(d['cagr']['1y'])} → {d['grade'][0]}, {d['consistency'][0]}")
    if debt:
        c = debt['current']
        print(f"Nợ vay {c['ky']}: {vn(c['no_vay']/1e9)} tỷ = {vn(c['lan_ln'] or 0, 2)} lần LN mẹ TTM → {debt['status'][0]}")
    if est:
        y = est['yoy']
        print(f"{est['year']} ước tính ({est['n']} quý × 4/{est['n']}): DT {vn(est['doanh_thu']/1e9)} tỷ ({pct(y['doanh_thu'])}), "
              f"EPS {vn(est['eps_pf'])} ({pct(y['eps_pf'])}), BVPS {vn(est['bvps_pf'] or 0)} ({pct(y['bvps_pf'])}), "
              f"CFO {vn((est['cfo'] or 0)/1e9)} tỷ ({pct(y['cfo'])}), ROIC {pct(est['roic'])}, ROE {pct(est['roe'])}")


LBL = {'bvps': ('2. Tăng BVPS', 'Giá trị sổ sách mỗi cổ phiếu'), 'sales': ('3. Tăng doanh thu', 'Doanh thu thuần'),
       'eps': ('4. Tăng EPS', 'Lợi nhuận mỗi cổ phiếu'), 'cash': ('5. Tăng dòng tiền', 'Dòng tiền kinh doanh CFO')}


def pill(s):
    return f'<span class="pill {s[1]}">{html.escape(s[0])}</span>'


def render(r, a):
    ys = [str(y) for y in r['years']]
    m1, G, D = r['roic_roe'], r['growth'], r['debt']
    rng = f"{ys[0]}→{ys[-1]}"
    # Bảng tóm tắt 6 mục
    s = []
    s.append(f"<tr><td><b>1. ROIC · ROE</b></td><td class=\"l\">ROIC {pct(min(v for v in m1['roic'].values() if v is not None))}–{pct(max(v for v in m1['roic'].values() if v is not None))}, "
             f"ROE {pct(min(v for v in m1['roe'].values() if v is not None))}–{pct(max(v for v in m1['roe'].values() if v is not None))} ({rng}); 4 quý gần nhất ROIC {pct(m1['roic_ttm'])}, ROE {pct(m1['roe_ttm'])}</td>"
             f"<td>≥ {vn(a.floor)}% mỗi năm</td><td>ROIC {pill(m1['roic_status'])}<br>ROE {pill(m1['roe_status'])}</td></tr>")
    for n in ('bvps', 'sales', 'eps', 'cash'):
        d = G[n]; c = d['cagr']
        s.append(f"<tr><td><b>{LBL[n][0]}</b></td><td class=\"l\">{pct(c['4y'])}/năm ({rng}); 3 năm {pct(c['3y'])}; năm gần nhất {pct(c['1y'])}</td>"
                 f"<td>≥ {vn(d['good'] * 100)}%/năm</td><td>{pill(d['grade'])}<br>{pill(d['consistency'])}</td></tr>")
    if D:
        c = D['current']
        s.append(f"<tr><td><b>6. Nợ vay</b></td><td class=\"l\">Nợ vay {vn(c['no_vay'] / 1e9)} tỷ ({c['ky']}) = <b>{vn(c['lan_ln'] or 0, 2)} lần</b> LN mẹ 4 quý; "
                 f"trừ tiền và đầu tư ngắn hạn còn {'tiền nhiều hơn nợ ' + vn(-c['no_vay_rong'] / 1e9) + ' tỷ' if c['no_vay_rong'] < 0 else vn(c['no_vay_rong'] / 1e9) + ' tỷ (' + vn(c['lan_ln_rong'], 2) + ' lần)'}</td>"
                 f"<td>≤ {vn(D['max'])} lần LN</td><td>{pill(D['status'])}</td></tr>")
    else:
        s.append("<tr><td><b>6. Nợ vay</b></td><td class=\"l\">Doanh nghiệp tài chính: nợ (tiền gửi, vay) là nguyên liệu kinh doanh, không so với lợi nhuận như doanh nghiệp thường.</td><td>—</td><td><span class=\"pill p-warn\">N/A</span></td></tr>")

    # Bảng chi tiết theo năm (+ cột năm đang dở ước tính nếu có)
    E = r.get('estimate')
    ex = (lambda txt: f"<td><i>{txt}</i></td>") if E else (lambda txt: '')
    sgn = lambda x: 'N/A' if x is None else ('+' if x > 0 else '') + pct(x)
    def rowp(lbl, ser, cls='', e=None, signed=False):
        return (f"<tr{cls}><td class=\"l\">{lbl}</td>" + ''.join(f"<td>{pct(ser.get(y))}</td>" for y in ys)
                + ex(sgn(e) if signed else pct(e)) + "</tr>")
    def rowv(lbl, ser, unit, e=None):
        f = (lambda v: vn(v / 1e9)) if unit == 'ty' else (lambda v: vn(v))
        return (f"<tr><td class=\"l\">{lbl}</td>" + ''.join(f"<td>{'N/A' if ser.get(y) is None else f(ser.get(y))}</td>" for y in ys)
                + ex('N/A' if e is None else f(e)) + "</tr>")
    g = (lambda k: E.get(k)) if E else (lambda k: None)
    gy = (lambda k: E['yoy'].get(k)) if E else (lambda k: None)
    det = [rowp('ROIC', m1['roic'], e=g('roic')), rowp('ROE', m1['roe'], e=g('roe'))]
    for n, unit, lbl in (('bvps', 'd', 'BVPS (đ, quy về cp hiện hành)'), ('sales', 'ty', 'Doanh thu (tỷ đ)'),
                         ('eps', 'd', 'EPS (đ, quy về cp hiện hành)'), ('cash', 'ty', 'CFO (tỷ đ)')):
        key = G[n]['key']
        det.append(rowv(lbl, G[n]['values'], unit, e=g(key)))
        det.append(rowp('&nbsp;&nbsp;tăng so với năm trước', G[n]['yoy'], ' class="chg"', e=gy(key), signed=True))
    if D:
        det.append(rowv('Nợ vay cuối năm (tỷ đ)', {y: D['hist'].get(y, {}).get('no_vay') for y in ys}, 'ty', e=g('no_vay')))
        det.append(f"<tr><td class=\"l\">&nbsp;&nbsp;nợ vay ÷ LN mẹ (lần)</td>" + ''.join(
            f"<td>{'N/A' if D['hist'].get(y, {}).get('lan_ln') is None else vn(D['hist'][y]['lan_ln'], 2)}</td>" for y in ys)
            + ex('N/A' if g('lan_ln') is None else vn(g('lan_ln'), 2)) + "</tr>")
    est_th = f"<th>{E['year']} ước tính*</th>" if E else ''
    est_note = ''
    if E:
        qs = '–'.join([E['quarters'][0], E['quarters'][-1]]) if E['n'] > 1 else E['quarters'][0]
        est_note = (f"<p class=\"note\">* <b>{E['year']} ước tính</b> = số {E['n']} quý đã công bố ({qs}) chia {E['n']} nhân 4: "
                    f"doanh thu {vn(E['rev_n'] / 1e9)} tỷ, LN mẹ {vn(E['ln_n'] / 1e9)} tỷ → LN mẹ cả năm ước {vn(E['ln_me'] / 1e9)} tỷ; "
                    f"CFO lũy kế {vn((E['cfo_ytd'] or 0) / 1e9)} tỷ. BVPS cuối năm = vốn chủ cuối {E['quarters'][-1]} + LN các quý còn lại ước tính"
                    + (f" − cổ tức tiền {vn(E['div_ps'])} đ/cp trả trước cuối năm" if E['div_ps'] else '')
                    + f"; nợ vay là số cuối {E['quarters'][-1]}. Đây là ước tính, chưa phải số báo cáo — mức Tốt/Khá/Yếu ở bảng trên vẫn chấm theo năm trọn vẹn {rng}.</p>")
        if a.est_note:
            est_note += f"\n  <div class=\"callout\"><b>Đọc cột {E['year']} ước tính:</b> {a.est_note}</div>"

    reason = ''
    if D and D['status'][0] == 'Xấu':
        reason = f"<div class=\"callout\"><strong>Vì sao nợ cao:</strong> {D['reason'] or '<i>chưa giải thích — cần bổ sung trước khi gửi báo cáo</i>'}</div>"
    return f"""<section class="card" id="bigfive">
  <h2>3b. 5 con số lớn và nợ (Phil Town)</h2>
  <p class="note">Kiểm tra doanh nghiệp hoạt động có tốt và đều không, theo quy tắc của chuyên gia. Số liệu năm {rng} từ CafeF; EPS, BVPS đã quy về số cổ phiếu hiện hành nên không bị lệch vì cổ tức cổ phiếu.</p>
  <div class="tw"><table>
    <tr><th>Mục</th><th>Số liệu</th><th>Mức tốt</th><th>Đánh giá</th></tr>
    {''.join(s)}
  </table></div>
  {reason}
  <div class="tw"><table>
    <tr><th>Chi tiết</th>{''.join(f'<th>{y}</th>' for y in ys)}{est_th}</tr>
    {''.join(det)}
  </table></div>
  {est_note}
  <div class="gloss">
    <div><b>ROIC</b> (Return on Invested Capital): lãi trên mỗi 100 đồng vốn đầu tư vào kinh doanh, cả vốn chủ lẫn vốn vay; tính bằng lãi kinh doanh cốt lõi sau thuế ÷ vốn sử dụng. <b>ROE</b>: lãi trên mỗi 100 đồng vốn chủ. Cả hai ≥ 10% mỗi năm là tốt.</div>
    <div><b>BVPS</b>: giá trị sổ sách mỗi cổ phiếu — phần tài sản thuộc về mỗi cổ phiếu. <b>EPS</b>: lợi nhuận mỗi cổ phiếu. <b>CFO</b>: tiền thực thu từ hoạt động kinh doanh.</div>
    <div><b>Tăng trưởng kép</b>: mức tăng đều mỗi năm. <b>Ổn định</b>: tăng trưởng kép 4 năm, 3 năm và năm gần nhất đều ≥ {vn(a.floor)}%; <b>Dao động</b>: có kỳ dưới {vn(a.floor)}% nhưng không giảm; <b>Không ổn định</b>: có kỳ giảm. <b>Tốt / Khá / Yếu</b>: đạt mức tốt / từ {vn(a.floor)}% tới dưới mức tốt / dưới {vn(a.floor)}%.</div>
    <div><b>Nợ vay</b>: vay ngân hàng và nợ thuê tài chính, ngắn và dài hạn (không tính tiền khách trả trước, phải trả người bán). <b>Nợ vay ÷ LN</b>: số năm lợi nhuận cần để trả hết nợ; trên {vn(a.debt_max)} lần là nợ nhiều.</div>
  </div>
</section>
"""


if __name__ == '__main__':
    main()
