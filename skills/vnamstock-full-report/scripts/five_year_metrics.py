"""Bang so sanh chi so 5 nam (CafeF) cho bao cao co ban VNamStock.

Run: python -I five_year_metrics.py --symbol FPT --out <ROOT>/FPT/BasicMetrics/<ngay>_vNN
     [--price 54000] [--shares 1885727648] [--ttm-ln-me 10280.7e9 --ttm-label "Q4/25–Q3/26"]
Xuat: five_year.json, five_year.csv, five_year_table.html (doan <section> dan vao dau bao cao), raw/*.json.
P/E, P/B cuoi nam tinh bang von hoa (gia dong cua chua dieu chinh x co phieu cuoi nam) / LN me hoac VCSH me,
nen khong bi lech do co phieu thuong. EPS, BVPS quy ve so co phieu hien hanh (pro forma) de so sanh cac nam.
Ngan hang/bao hiem: schema CafeF khac, cac dong thieu ma se ra N/A - can bo sung tay.
"""
import argparse, csv, json, os, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://cafef.vn/'}
API = 'https://apiweb.cafef.vn/api/v1/BCTC'


def get(url, raw_dir, name):
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30))
            json.dump(d, open(os.path.join(raw_dir, name), 'w', encoding='utf-8'), ensure_ascii=False)
            return d
        except Exception as e:
            err = e
    raise err


def periods(resp):
    """{time: {code: value}} gop tat ca khoi (KQKD, CDKT, HDKD...)."""
    out = {}
    for blk in resp['value']['data']:
        for p in blk['data']:
            out.setdefault(p['time'], {}).update({x['code']: x['value'] for x in p['data']})
    return out


def year_end_close(sym, y, raw_dir):
    u = f'https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx?Symbol={sym}&StartDate=12/01/{y}&EndDate=12/31/{y}&PageIndex=1&PageSize=30'
    rows = get(u, raw_dir, f'price_{y}12.json')['Data']['Data']
    return (rows[0]['GiaDongCua'] * 1000, rows[0]['Ngay']) if rows else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--symbol', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--price', type=float, help='gia hien tai d/cp; mac dinh lay phien gan nhat CafeF')
    ap.add_argument('--shares', type=float, help='co phieu luu hanh hien tai; mac dinh von gop quy gan nhat / 10.000')
    ap.add_argument('--ttm-ln-me', type=float, help='LN me 4 quy gan nhat (d) neu CafeF chua co quy moi')
    ap.add_argument('--ttm-label', help='nhan ky TTM khi dung --ttm-ln-me')
    ap.add_argument('--section-class', default='card price-top', help='class cua <section>; bao cao tong hop dung "card"')
    a = ap.parse_args()
    sym = a.symbol.upper()
    raw = os.path.join(a.out, 'raw'); os.makedirs(raw, exist_ok=True)

    yr = {}
    for p in (1, 2):
        yr.update(periods(get(f'{API}/GetReportSummary?symbol={sym}&pageIndex={p}&pageSize=4&reportType=ALL&TypeTime=NAM', raw, f'summary_NAM_p{p}.json')))
        yr_cf = periods(get(f'{API}/GetReportLCTT?symbol={sym}&pageIndex={p}&pageSize=4&reportType=ALL&TypeTime=NAM', raw, f'lctt_NAM_p{p}.json'))
        for t, v in yr_cf.items(): yr.setdefault(t, {}).update(v)
    q = {}
    for p in (1, 2):
        q.update(periods(get(f'{API}/GetReportSummary?symbol={sym}&pageIndex={p}&pageSize=4&reportType=ALL&TypeTime=QUY', raw, f'summary_QUY_p{p}.json')))
    qkeys = sorted(q, key=lambda t: (int(t.split('-')[1]), int(t[1])))   # 'Q2-2026'

    years = sorted(int(t) for t in yr if t.isdigit())
    last = years[-1]; cols = list(range(last - 4, last + 1))

    v = lambda d, c: (d or {}).get(c)
    eq_me = lambda d: None if v(d, 'CDKT_31') is None else v(d, 'CDKT_31') - (v(d, 'CDKT_35') or 0)
    div = lambda x, y: None if x is None or not y else x / y
    avg = lambda x, y: None if x is None or y is None else (x + y) / 2

    lq = q[qkeys[-1]]
    shares_now = a.shares or v(lq, 'CDKT_32') / 1e4
    if a.price:
        price_now, price_date = a.price, 'nhập tay'
    else:
        r = get(f'https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx?Symbol={sym}&PageIndex=1&PageSize=1', raw, 'price_now.json')['Data']['Data'][0]
        price_now, price_date = r['GiaDongCua'] * 1000, r['Ngay']

    rows = {}
    for y in cols:
        d, d0 = yr.get(str(y)), yr.get(str(y - 1))
        rev, ln = v(d, 'KQKD_2'), v(d, 'KQKD_14')
        e, e0 = eq_me(d), eq_me(d0)
        px, pdate = year_end_close(sym, y, raw)
        sh_ye = v(d, 'CDKT_32') / 1e4 if v(d, 'CDKT_32') else None
        mcap = px * sh_ye if px and sh_ye else None
        cfo, capex, dps_paid = v(d, 'HDKD_20') or None, v(d, 'HDDT_22') or None, v(d, 'HDTC_36')   # CFO/capex 0 = CafeF thieu so lieu
        rows[str(y)] = {
            'doanh_thu': rev, 'dt_yoy': div(rev, v(d0, 'KQKD_2')) and div(rev, v(d0, 'KQKD_2')) - 1,
            'ln_me': ln, 'ln_yoy': div(ln, v(d0, 'KQKD_14')) and div(ln, v(d0, 'KQKD_14')) - 1,
            'bien_gop': div(v(d, 'KQKD_4'), rev), 'bien_rong': div(ln, rev),
            'roe': div(ln, avg(e, e0)), 'roa': div(ln, avg(v(d, 'CDKT_27'), v(d0, 'CDKT_27'))),
            'eps_pf': div(ln, shares_now), 'bvps_pf': div(e, shares_now), 'eps_cafef': v(d, 'KQKD_15'),
            'gia_cuoi_nam': px, 'ngay_gia': pdate, 'von_hoa': mcap,
            'pe': div(mcap, ln), 'pb': div(mcap, e),
            'no_vcsh': div(v(d, 'CDKT_28'), v(d, 'CDKT_31')),
            'no_phai_tra': v(d, 'CDKT_28'), 'no_dt': div(v(d, 'CDKT_28'), rev),
            'cfo': cfo, 'cfo_ln': div(cfo, ln), 'fcf': None if cfo is None or capex is None else cfo + capex,
            'co_tuc_yield': div(-dps_paid if dps_paid else None, mcap),
        }

    # TTM / hien tai
    last4 = qkeys[-4:]
    ttm_ln = a.ttm_ln_me or sum(v(q[t], 'KQKD_14') or 0 for t in last4)
    ttm_rev = sum(v(q[t], 'KQKD_2') or 0 for t in last4)
    e_now = eq_me(lq)
    e_4ago = eq_me(q[qkeys[-5]]) if len(qkeys) >= 5 else None
    mcap_now = price_now * shares_now
    cafef_label = f'{last4[0]}→{last4[-1]}'
    ttm_label = a.ttm_label or cafef_label
    rows['TTM'] = {
        'doanh_thu': ttm_rev, 'ln_me': ttm_ln, 'bien_gop': div(sum(v(q[t], 'KQKD_4') or 0 for t in last4), ttm_rev),
        'bien_rong': div(sum(v(q[t], 'KQKD_14') or 0 for t in last4), ttm_rev),  # cung ky voi doanh thu CafeF
        'roe': div(ttm_ln, avg(e_now, e_4ago)), 'roa': div(ttm_ln, avg(v(lq, 'CDKT_27'), v(q[qkeys[-5]], 'CDKT_27') if len(qkeys) >= 5 else None)),
        'eps_pf': ttm_ln / shares_now, 'bvps_pf': div(e_now, shares_now),
        'gia_cuoi_nam': price_now, 'ngay_gia': price_date, 'von_hoa': mcap_now,
        'pe': div(mcap_now, ttm_ln), 'pb': div(mcap_now, e_now), 'no_vcsh': div(v(lq, 'CDKT_28'), v(lq, 'CDKT_31')),
        'no_phai_tra': v(lq, 'CDKT_28'), 'no_dt': div(v(lq, 'CDKT_28'), ttm_rev),
    }

    def cagr(k):
        a0, a1 = rows[str(cols[0])].get(k), rows[str(cols[-1])].get(k)
        return (a1 / a0) ** (1 / 4) - 1 if a0 and a1 and a0 > 0 and a1 > 0 else None

    def mean(k):
        xs = [rows[str(y)].get(k) for y in cols if rows[str(y)].get(k) is not None]
        return sum(xs) / len(xs) if xs else None

    summary = {k: ('CAGR', cagr(k)) for k in ('doanh_thu', 'ln_me', 'eps_pf', 'bvps_pf', 'no_phai_tra')}
    summary.update({k: ('TB', mean(k)) for k in ('dt_yoy', 'ln_yoy', 'bien_gop', 'bien_rong', 'roe', 'roa', 'pe', 'pb', 'no_vcsh', 'no_dt', 'cfo_ln', 'co_tuc_yield')})

    meta = {'symbol': sym, 'years': cols, 'ttm_label': ttm_label, 'price_now': price_now, 'price_date': price_date,
            'shares_now': shares_now, 'latest_quarter': qkeys[-1], 'ttm_ln_override': bool(a.ttm_ln_me), 'cafef_ttm_label': cafef_label}
    json.dump({'meta': meta, 'rows': rows, 'summary': summary}, open(os.path.join(a.out, 'five_year.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    keys = list(rows[str(cols[0])])
    with open(os.path.join(a.out, 'five_year.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['chi_tieu'] + [str(c) for c in cols] + ['TTM', 'tong_hop'])
        for k in keys:
            s = summary.get(k)
            w.writerow([k] + [rows[str(c)].get(k) for c in cols] + [rows['TTM'].get(k), f'{s[0]} {s[1]}' if s else ''])

    open(os.path.join(a.out, 'five_year_table.html'), 'w', encoding='utf-8').write(render(meta, rows, summary, cols, a.section_class))
    print(json.dumps(meta, ensure_ascii=False))
    for k in keys:
        print(f'{k:13}', ' | '.join(fmt(k, rows[str(c)].get(k)) for c in cols), '| TTM', fmt(k, rows['TTM'].get(k)), '|', summary.get(k))


# ---------- HTML ----------
PCT = {'dt_yoy', 'ln_yoy', 'bien_gop', 'bien_rong', 'roe', 'roa', 'co_tuc_yield', 'no_dt'}
TY = {'doanh_thu', 'ln_me', 'von_hoa', 'cfo', 'fcf', 'no_phai_tra'}
X = {'pe', 'pb', 'no_vcsh', 'cfo_ln'}


def vn(x, nd=0):
    s = f'{x:,.{nd}f}'
    return s.replace(',', '§').replace('.', ',').replace('§', '.')


def fmt(k, x):
    if x is None or isinstance(x, str): return x or 'N/A'
    if k in PCT: return vn(x * 100, 1) + '%'
    if k in TY: return vn(x / 1e9)
    if k in X: return vn(x, 2 if k in ('no_vcsh', 'pb') else 1)
    return vn(x)


LAYOUT = [
    ('Tăng trưởng', [('doanh_thu', 'Doanh thu thuần (tỷ đ)'), ('dt_yoy', 'Doanh thu so năm trước'),
                     ('ln_me', 'LN mẹ (tỷ đ)'), ('ln_yoy', 'LN mẹ so năm trước')]),
    ('Hiệu quả', [('bien_gop', 'Biên lợi nhuận gộp'), ('bien_rong', 'Biên LN ròng (LN mẹ/doanh thu)'),
                  ('roe', 'ROE'), ('roa', 'ROA')]),
    ('Mỗi cổ phiếu (quy về cp hiện hành)', [('eps_pf', 'EPS (đ)'), ('bvps_pf', 'BVPS (đ)')]),
    ('Định giá tại giá cuối năm', [('gia_cuoi_nam', 'Giá đóng cửa (đ, chưa điều chỉnh)'), ('pe', 'P/E (lần)'),
                                   ('pb', 'P/B (lần)'), ('co_tuc_yield', 'Tỷ suất cổ tức tiền đã trả')]),
    ('Sức khỏe tài chính', [('no_phai_tra', 'Tổng nợ phải trả cuối kỳ (tỷ đ)'), ('no_dt', 'Nợ phải trả / Doanh thu'),
                            ('no_vcsh', 'Nợ phải trả / VCSH (lần)'), ('cfo', 'Dòng tiền kinh doanh CFO (tỷ đ)'),
                            ('cfo_ln', 'CFO / LN mẹ (lần)'), ('fcf', 'FCF = CFO − đầu tư TSCĐ (tỷ đ)')]),
]


def render(meta, rows, summary, cols, cls='card price-top'):
    head = ''.join(f'<th>{c}</th>' for c in cols)
    body = []
    for grp, items in LAYOUT:
        body.append(f'<tr class="grp"><td colspan="{len(cols) + 3}">{grp}</td></tr>')
        for k, label in items:
            vals = ''.join(f'<td>{fmt(k, rows[str(c)].get(k))}</td>' for c in cols)
            if all(rows[str(c)].get(k) is None for c in cols) and rows['TTM'].get(k) is None: continue
            t = rows['TTM'].get(k)
            s = summary.get(k)
            stxt = '—' if not s or s[1] is None else f'{s[0]} {fmt(k if k not in ("doanh_thu", "ln_me", "eps_pf", "bvps_pf", "no_phai_tra") else "dt_yoy", s[1])}'
            body.append(f'<tr><td>{label}</td>{vals}<td><b>{fmt(k, t) if t is not None else "—"}</b></td><td>{stxt}</td></tr>')
    return f'''<section class="{cls}" id="namnam">
  <h2>So sánh chỉ số 5 năm ({cols[0]}–{cols[-1]})</h2>
  <div class="tw"><table class="fy">
    <tr><th>Chỉ số</th>{head}<th>TTM / hiện tại</th><th>CAGR · TB 5 năm</th></tr>
    {"".join(body)}
  </table></div>
  <p class="note">Năm = báo cáo hợp nhất cả năm (CafeF). Cột TTM: LN mẹ, EPS, ROE, P/E theo 4 quý {meta["ttm_label"]}{"" if not meta["ttm_ln_override"] else "; doanh thu và biên theo 4 quý CafeF " + meta["cafef_ttm_label"]}; giá {vn(meta["price_now"])} đ ({meta["price_date"]}). P/E, P/B mỗi năm = vốn hóa cuối năm ÷ LN mẹ / VCSH mẹ, nên không bị lệch do cổ phiếu thưởng.</p>
  <div class="gloss">
    <div><b>LN mẹ</b>: lợi nhuận sau thuế thuộc cổ đông công ty mẹ. <b>Biên LN gộp</b>: phần lãi còn lại sau giá vốn trên mỗi 100 đồng doanh thu. <b>ROE</b>: lãi trên mỗi 100 đồng vốn chủ. <b>ROA</b>: lãi trên mỗi 100 đồng tài sản.</div>
    <div><b>EPS · BVPS</b>: lợi nhuận · giá trị sổ sách mỗi cổ phiếu, chia cho số cổ phiếu hiện tại để các năm so được với nhau. <b>P/E · P/B</b>: giá gấp bao nhiêu lần lợi nhuận · giá trị sổ sách.</div>
    <div><b>Nợ phải trả / Doanh thu</b>: tổng nợ cuối kỳ bằng bao nhiêu % doanh thu cả năm — tăng dần qua các năm nghĩa là nợ phình nhanh hơn việc kinh doanh. <b>VCSH</b>: vốn chủ sở hữu. <b>CFO</b>: tiền thật thu từ kinh doanh; CFO/LN mẹ ≥ 1 là lợi nhuận về tiền tốt. <b>FCF</b>: dòng tiền tự do còn lại sau đầu tư tài sản cố định. <b>TTM</b>: 12 tháng gần nhất. <b>CAGR</b>: tăng trưởng kép bình quân mỗi năm. <b>TB</b>: trung bình 5 năm.</div>
  </div>
</section>
'''


if __name__ == '__main__':
    main()
