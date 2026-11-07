#!/usr/bin/env python3
"""Kế hoạch mua bán cổ phiếu 5-10 năm: cổ tức tiền + cổ tức cổ phiếu, luôn tái đầu tư, bán ở giá định trước.

Mô hình (luôn tái đầu tư cổ tức, 02/11/2026):
- Mỗi năm, trên số cp đầu năm: nhận cổ phiếu thưởng (× stock_pct) và tiền mặt (× DPS);
  tiền mặt mua thêm cp ở giá mua -> số cp × (1 + stock_pct + DPS/giá mua) mỗi năm.
- Tổng tiền khi bán = số cp cuối kỳ × giá bán.
- Giá bán ↔ năm giữ: số năm (lẻ) để tổng tiền ở giá bán X bằng tổng tiền khi bán giá mốc sau N năm,
  tính theo giá vốn.
Chưa trừ thuế trong bảng; ước tính thuế riêng cho dòng giá vốn.
"""
import argparse, json, math, os, html, datetime

PAR = 10000


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def tr(x):  # đồng -> "12,3 tr" hoặc "1,01 tỷ"
    return vn(x / 1e9, 2) + " tỷ" if abs(x) >= 1e9 else vn(x / 1e6, 1) + " tr"


def pct(x, d=0, sign=True):
    return ("+" if sign and x >= 0 else "") + vn(x * 100, d) + "%"


def nice_step(x):
    """Làm tròn bước giá về 1/2/5 × 10^k (vd 5.270 -> 5.000)."""
    m = 10 ** math.floor(math.log10(x))
    return min((1, 2, 5, 10), key=lambda k: abs(k * m - x)) * m


def sim(sh0, P, dps, s, n, sell, dg=0.0):
    """dg: tốc độ tăng cổ tức tiền mặt đ/cp mỗi năm (năm 1 = dps)."""
    sh, cash, bonus = sh0, 0.0, 0.0
    for t in range(n):
        c, b = sh * dps * (1 + dg) ** t, sh * s
        cash += c
        bonus += b
        sh += b + c / P
    cost, V = sh0 * P, sh * sell
    return dict(cost=cost, sh=sh, cash=cash, bonus=bonus, V=V, tot=V / cost - 1, cagr=(V / cost) ** (1 / n) - 1)


def years_equiv(g, n0, S0, X):
    """Số năm để sh0·(1+g)^n·X = sh0·(1+g)^n0·S0."""
    if g <= 0:
        return None if X < S0 else n0
    y = n0 + math.log(S0 / X) / math.log(1 + g)
    return y if 0 <= y <= 40 else None


def ym(y):
    if y is None:
        return "> 40 năm"
    m = round(y * 12)
    a, b = divmod(m, 12)
    if b == 0:
        return f"{a} năm"
    return f"{a} năm {b} tháng" if a else f"{b} tháng"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--name", default="")
    ap.add_argument("--buy-price", type=float, required=True, help="giá vốn bình quân (đ/cp)")
    ap.add_argument("--shares", type=float, required=True, help="số cp đang nắm")
    ap.add_argument("--dps", type=float, required=True, help="cổ tức tiền mặt đ/cp/năm")
    ap.add_argument("--stock-pct", type=float, required=True, help="cổ tức cổ phiếu %%/năm, vd 10")
    ap.add_argument("--sell-price", type=float, required=True, help="giá định bán ở năm mốc (đ/cp)")
    ap.add_argument("--sell-price-long", type=float, help="giá định bán ở năm dài hạn; mặc định = --sell-price")
    ap.add_argument("--anchor-years", type=int, default=5)
    ap.add_argument("--long-years", type=int, default=10)
    ap.add_argument("--buy-ladder", help="danh sách giá mua so sánh, vd 70000,60000,50000")
    ap.add_argument("--market-price", type=float, help="giá thị trường hiện tại")
    ap.add_argument("--market-date", default="")
    ap.add_argument("--shares-out", type=float, help="số cp lưu hành hiện tại (triệu cp) để kiểm tra khả thi")
    ap.add_argument("--ttm-profit", type=float, help="LN mẹ 4 quý gần nhất (tỷ đ)")
    ap.add_argument("--pe-assume", type=float, default=15.0)
    ap.add_argument("--add-amount", type=float, help="số tiền định đầu tư thêm (đồng), vd 100000000")
    ap.add_argument("--lot", type=int, default=100, help="lô chẵn khi mua thêm (HOSE 100 cp)")
    ap.add_argument("--div-note", default="", help="nguồn/căn cứ giả định cổ tức (HTML được phép)")
    ap.add_argument("--sources", default="", help="nguồn, phân cách bởi ' | ', dạng 'tên::url'")
    # Kịch bản cổ tức (thêm 06/11/2026)
    ap.add_argument("--dps-growth", type=float, default=0.0, help="cổ tức tiền mặt tăng %%/năm cho bảng chính, vd 10")
    ap.add_argument("--div-scenarios", default="", help="'tên:đ/cp:%%cp[:%%tăng tiền]; ...' — bảng so sánh kịch bản cổ tức")
    ap.add_argument("--div-history", default="", help="'thời điểm|tiền|cổ phiếu|ghi chú; ...' — bảng lịch sử cổ tức (HTML được phép)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--out", required=True, help="đường dẫn file HTML")
    # Kelly (thêm 06/11/2026 theo yêu cầu)
    ap.add_argument("--kelly-p", type=float, help="xác suất (0-1) giá lên mức --kelly-up; bật mục Kelly")
    ap.add_argument("--kelly-up", type=float, help="giá nếu đúng (mặc định = --sell-price)")
    ap.add_argument("--kelly-down", type=float, help="giá nếu sai (đ/cp)")
    ap.add_argument("--buy-zone", help="vùng mua dự kiến 'thấp-cao', vd 28000-30000")
    ap.add_argument("--planned", action="store_true", help="chưa mua: gọi --buy-price là 'giá mua dự kiến', --shares là số cp minh họa")
    ap.add_argument("--value-notes", default="", help="đối chiếu giá trị/định giá (HTML), hiện trong mục Kelly")
    a = ap.parse_args()

    s = a.stock_pct / 100
    dg = a.dps_growth / 100
    S5 = a.sell_price
    S10 = a.sell_price_long or a.sell_price
    N5, N10 = a.anchor_years, a.long_years
    sh0, P0 = a.shares, a.buy_price

    if a.buy_ladder:
        ladder = [float(x) for x in a.buy_ladder.split(",")]
    else:
        # Bậc giá tròn từ trên giá vốn/giá thị trường xuống dưới nửa giá thị trường (để lên kế hoạch mua thêm).
        ref = a.market_price or P0
        step = nice_step(ref * 0.1)
        top = math.ceil(max(P0, ref) * 1.2 / step) * step
        floor_ = ref / 2
        ladder, p = [], top
        while True:
            ladder.append(p)
            if p < floor_:
                break
            p -= step
    ladder = set(ladder) | {P0}
    if a.market_price:
        ladder.add(a.market_price)
    zone = None
    if a.buy_zone:
        zone = tuple(float(x) for x in a.buy_zone.split("-"))
        ladder |= set(zone)
    ladder = sorted(ladder, reverse=True)
    ME = "giá mua dự kiến" if a.planned else "giá vốn"

    def tag(P):
        t = []
        if P == P0:
            t.append(ME)
        elif zone and zone[0] <= P <= zone[1]:
            t.append("vùng mua")
        if a.market_price and P == a.market_price:
            t.append("giá thị trường")
        return t

    rows = []
    for P in ladder:
        r = dict(P=P, tags=tag(P), t1=sim(sh0, P, a.dps, s, N5, P, dg),
                 t2=sim(sh0, P, a.dps, s, N5, S5, dg), t3=sim(sh0, P, a.dps, s, N10, S10, dg), add=None)
        if a.add_amount:
            n_add = math.floor(a.add_amount / P / a.lot) * a.lot
            if n_add > 0:
                r["add"] = dict(n=n_add, t2=sim(n_add, P, a.dps, s, N5, S5, dg), t3=sim(n_add, P, a.dps, s, N10, S10, dg))
        rows.append(r)

    me = next(r for r in rows if r["P"] == P0)
    g0 = s + a.dps / P0
    ytabs = []  # giá bán ↔ số năm giữ, mốc 5 năm và mốc 10 năm
    for key, n0, S0 in (("t2", N5, S5), ("t3", N10, S10)):
        t = []
        for m in (1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7):
            X = round(S0 * m / 1000) * 1000
            y = n0 if m == 1.0 else years_equiv(g0, n0, S0, X)
            t.append(dict(sell=X, years=y, diff=None if y is None else y - n0))
        ytabs.append(dict(n=n0, S=S0, target=me[key]["V"], cost=me[key]["cost"], rows=t))
    target = ytabs[0]["target"]

    def tax(key, sell):
        r = me[key]
        t_cash = 0.05 * r["cash"]
        t_sale = 0.001 * r["V"]
        t_bonus = 0.05 * PAR * r["bonus"]
        return dict(cash=t_cash, sale=t_sale, bonus=t_bonus, total=t_cash + t_sale + t_bonus,
                    net=r["V"] - t_cash - t_sale - t_bonus, cost=r["cost"])

    taxes = {N5: tax("t2", S5), N10: tax("t3", S10)}

    feas, cur_pe = [], None
    if a.shares_out and a.ttm_profit:
        if a.market_price:
            eps = a.ttm_profit * 1e9 / (a.shares_out * 1e6)
            cur_pe = a.market_price / eps
        for n, S in ((N5, S5), (N10, S10)):
            eq = S * (1 + s) ** n
            cap = eq * a.shares_out * 1e6 / 1e9  # tỷ đ
            g = lambda pe: (cap / pe / a.ttm_profit) ** (1 / n) - 1
            feas.append(dict(n=n, S=S, eq=eq, cap=cap, g_pe=g(a.pe_assume), g_cur=g(cur_pe) if cur_pe else None))

    kel = kelly_block(a, ladder, P0, zone, N5) if a.kelly_p is not None and a.kelly_down else None
    divsc = div_scenarios(a, sh0, P0, S5, S10, N5, N10)

    data = dict(inputs=vars(a), ladder=ladder, rows=rows, target=target, table_years=ytabs, taxes=taxes,
                feasibility=feas, current_pe=cur_pe, kelly=kel, div_scenarios=divsc)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(os.path.splitext(a.out)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, default=str)

    with open(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.abspath(a.out), "w", encoding="utf-8") as f:
        f.write(render(a, css, rows, me, ytabs, taxes, feas, cur_pe, target, s, S5, S10, N5, N10, sh0, P0, kel, divsc))
    print(a.out)


def div_scenarios(a, sh0, P0, S5, S10, N5, N10):
    """So sánh kịch bản cổ tức trên vị thế đang giữ (giá vốn P0). Kèm 'tương đương giá hôm nay' và LN cần tăng/năm."""
    if not a.div_scenarios.strip():
        return None
    out = []
    for item in a.div_scenarios.split(";"):
        if not item.strip():
            continue
        parts = [x.strip() for x in item.split(":")]
        name, dps, sp = parts[0], float(parts[1]), float(parts[2]) / 100
        dg = float(parts[3]) / 100 if len(parts) > 3 and parts[3] else 0.0
        r5, r10 = sim(sh0, P0, dps, sp, N5, S5, dg), sim(sh0, P0, dps, sp, N10, S10, dg)
        row = dict(name=name, dps=dps, stock=sp, dg=dps and dg, t5=r5, t10=r10,
                   dps_last5=dps * (1 + dg) ** (N5 - 1), yield1=dps / P0)
        if a.shares_out and a.ttm_profit:
            for n, S, key in ((N5, S5, "g5"), (N10, S10, "g10")):
                cap = S * (1 + sp) ** n * a.shares_out * 1e6 / 1e9
                row[key] = (cap / a.pe_assume / a.ttm_profit) ** (1 / n) - 1
                row["eq" + key[1:]] = S * (1 + sp) ** n
        out.append(row)
    hist = []
    for item in a.div_history.split(";"):
        if item.strip():
            hist.append([x.strip() for x in item.split("|")] + [""] * 3)
    return dict(rows=out, hist=hist)


def render_divsc(a, d, P0, S5, S10, N5, N10):
    hist = ""
    if d["hist"]:
        hr = "".join(f"<tr><td>{h[0]}</td><td>{h[1] or '—'}</td><td>{h[2] or '—'}</td><td class='l'>{h[3]}</td></tr>" for h in d["hist"])
        hist = f"""<h2 style="font-size:16px">Lịch sử cổ tức đã trả</h2>
<div class="tw"><table><tr><th>Thời điểm</th><th>Tiền mặt</th><th>Cổ phiếu</th><th>Ghi chú</th></tr>{hr}</table></div>"""
    has_g = any("g5" in r for r in d["rows"])
    rows = []
    for r in d["rows"]:
        main = abs(r["dps"] - a.dps) < 1e-9 and abs(r["stock"] - a.stock_pct / 100) < 1e-9 and abs(r["dg"] - a.dps_growth / 100) < 1e-9
        cash = f"{vn(r['dps'])} đ" + (f" → {vn(r['dps_last5'])} đ (+{vn(r['dg'] * 100, 0)}%/năm)" if r["dg"] else "")
        g = f"<td>{vn(r['eq5'])} đ</td><td><b>{pct(r['g5'], 1, False)}</b></td>" if has_g else ""
        rows.append(f"<tr{' class=\"me\"' if main else ''}><td class='l'>{e_(r['name'])}{' <span class=\"pill p-acc\">bảng chính</span>' if main else ''}</td>"
                    f"<td>{cash}</td><td>{vn(r['stock'] * 100, 2 if r['stock'] * 100 % 1 else 0)}%</td><td>{vn(r['t5']['sh'])}</td>"
                    f"<td><b>{tr(r['t5']['V'])}</b> ({pct(r['t5']['tot'])})</td><td>~{pct(r['t5']['cagr'], 1, False)}</td>"
                    f"<td><b>{tr(r['t10']['V'])}</b> ({pct(r['t10']['tot'])})</td>{g}</tr>")
    gh = f"<th>Giá {vn(S5)} đ sau {N5} năm tương đương hôm nay</th><th>LN cần tăng/năm (P/E {vn(a.pe_assume, 1)}, {N5} năm)</th>" if has_g else ""
    return f"""<section class="card" id="cotuc"><h2>Kịch bản cổ tức — kết quả thay đổi thế nào?</h2>
<p class="sub">Cùng vị thế {vn(a.shares)} cp, {'giá mua dự kiến' if a.planned else 'giá vốn'} {vn(P0)} đ, bán {vn(S5)} đ sau {N5} năm / {vn(S10)} đ sau {N10} năm, luôn tái đầu tư cổ tức. Các bảng 1–{'7' if a.add_amount else '5'} bên dưới dùng dòng “bảng chính”.</p>
{hist}
<div class="tw" style="margin-top:12px"><table><tr><th>Kịch bản</th><th>Tiền mặt/cp (năm 1 → năm {N5})</th><th>Cổ phiếu/năm</th><th>Số cp sau {N5} năm</th><th>Bán sau {N5} năm</th><th>Lãi kép/năm</th><th>Bán sau {N10} năm</th>{gh}</tr>
{''.join(rows)}</table></div>
<div class="callout"><b>Đọc đúng:</b> chia nhiều cổ phiếu hơn làm số cp tăng, nhưng mỗi lần chia giá được điều chỉnh giảm tương ứng — tự nó không tạo ra tiền. Kịch bản chia nhiều cổ phiếu chỉ đúng khi lợi nhuận công ty tăng đủ nhanh để giá vẫn lên {vn(S5)} đ trên số cổ phiếu lớn hơn (cột “LN cần tăng/năm”). Cổ tức tiền tăng dần là điều tốt thật, nhưng phải có lợi nhuận và vốn đủ để trả.</div>
<div class="gloss"><div><b>Tương đương hôm nay</b>: giá bán × số lần cổ phiếu đã nhân lên do chia thưởng, để so với giá hiện tại. <b>LN cần tăng/năm</b>: tốc độ lợi nhuận phải tăng để vốn hóa ở P/E giả định đạt mức giá bán. <b>Lãi kép/năm</b>: mức tăng đều mỗi năm của vốn. <b>P/E</b>: giá ÷ lợi nhuận mỗi cổ phiếu. Trước thuế.</div></div>
</section>
"""


def e_(x):
    return html.escape(x)


def zone_of(a):
    return tuple(float(x) for x in a.buy_zone.split("-")) if a.buy_zone else None


def kelly(p, up, down, P):
    """Kelly cho 2 kết cục: giá về `up` (xác suất p) hoặc `down` (1-p), mua ở P.
    b = lãi/đồng nếu đúng, l = lỗ/đồng nếu sai; f* = p/l - (1-p)/b (tỷ lệ vốn tối ưu, Thorp)."""
    b, l = up / P - 1, 1 - down / P
    ev = p * b - (1 - p) * l
    if b <= 0:
        return dict(P=P, b=b, l=l, ev=ev, f=0.0, p0=None)
    f = 1.0 if l <= 0 else p / l - (1 - p) / b
    return dict(P=P, b=b, l=l, ev=ev, f=f, p0=None if l <= 0 else l / (l + b))


def growth(p, b, l, f):
    """Tăng trưởng log kỳ vọng cả kỳ khi đặt f vốn (f ≤ 1, không vay)."""
    if f <= 0:
        return 0.0
    if 1 - f * l <= 0:
        return None
    return p * math.log(1 + f * b) + (1 - p) * math.log(1 - f * l)


def kelly_block(a, ladder, P0, zone, N):
    p, up, dn = a.kelly_p, a.kelly_up or a.sell_price, a.kelly_down
    rows = []
    for P in ladder:
        if P <= dn or P >= up:
            continue
        k = kelly(p, up, dn, P)
        for name, m in (("full", 1.0), ("half", 0.5), ("quarter", 0.25)):
            fc = max(0.0, min(1.0, k["f"] * m))          # không dùng margin: trần 100%
            k[name] = fc
            g = growth(p, k["b"], k["l"], fc)
            k["g_" + name] = None if g is None else math.exp(g / N) - 1
        rows.append(k)
    mid = (zone[0] + zone[1]) / 2 if zone else P0
    ps = [round(p + d, 2) for d in (-0.2, -0.1, -0.05, 0.0, 0.05, 0.1) if 0 < p + d < 1]
    downs = sorted({dn, round(dn * 0.75, -3), round(dn * 1.2, -3), round(dn * 1.35, -3)})
    downs = [d for d in downs if d < mid]
    sens = [dict(p=pp, cells=[kelly(pp, up, d, mid)["f"] for d in downs]) for pp in ps]
    ups = sorted({up, round(up * 0.8, -3), round(up * 0.9, -3), round(up * 1.1, -3)})
    sens_up = [dict(up=u, f=kelly(p, u, dn, mid)["f"], ev=kelly(p, u, dn, mid)["ev"]) for u in ups]
    return dict(p=p, up=up, down=dn, mid=mid, rows=rows, downs=downs, sens=sens, sens_up=sens_up, N=N)


def label(r):
    t = " ".join(f'<span class="pill p-acc">{x}</span>' for x in r["tags"])
    return f"{vn(r['P'])} {t}"


def trc(r):
    return ' class="me"' if ("giá vốn" in r["tags"] or "giá mua dự kiến" in r["tags"]) else (' class="mk"' if r["tags"] else "")


def render_kelly(a, kel, P0, zone):
    p, up, dn, N = kel["p"], kel["up"], kel["down"], kel["N"]
    q = 1 - p
    fmt_f = lambda f: ("<span class='neg'>0% (không mua)</span>" if f <= 0 else (f"<b>{vn(f * 100, 0)}%</b>" + (" <span class='pill p-acc'>&gt;100%: cần vay</span>" if f > 1 else "")))
    rows = []
    for k in kel["rows"]:
        P = k["P"]
        cls = ' class="me"' if P == P0 else (' class="mk"' if (zone and zone[0] <= P <= zone[1]) or (a.market_price and P == a.market_price) else "")
        tagt = "giá mua dự kiến" if (P == P0 and a.planned) else ("giá vốn" if P == P0 else ("giá thị trường" if a.market_price and P == a.market_price else ("vùng mua" if zone and zone[0] <= P <= zone[1] else "")))
        t = f' <span class="pill p-acc">{tagt}</span>' if tagt else ""
        g = lambda x: "—" if x is None else ("~" + pct(x, 1, False))
        rows.append(f"<tr{cls}><td>{vn(P)}{t}</td><td class='pos'>{pct(k['b'])}</td><td class='neg'>−{vn(k['l'] * 100, 0)}%</td>"
                    f"<td class='{'pos' if k['ev'] > 0 else 'neg'}'>{pct(k['ev'])}</td><td>{fmt_f(k['f'])}</td><td>{vn(k['half'] * 100, 0)}%</td>"
                    f"<td>{vn(k['quarter'] * 100, 0)}%</td><td>{g(k['g_half'])}</td><td>{'—' if k['p0'] is None else vn(k['p0'] * 100, 0) + '%'}</td></tr>")
    head = "".join(f"<th>Giá sai {vn(d)} đ</th>" for d in kel["downs"])
    srows = "".join(f"<tr{' class=\"me\"' if abs(r['p'] - p) < 1e-9 else ''}><td>{vn(r['p'] * 100, 0)}% lên {vn(up)}</td>" + "".join(f"<td>{fmt_f(c)}</td>" for c in r["cells"]) + "</tr>" for r in kel["sens"])
    urows = "".join(f"<tr{' class=\"me\"' if u['up'] == up else ''}><td>{vn(u['up'])}</td><td>{fmt_f(u['f'])}</td><td class='{'pos' if u['ev'] > 0 else 'neg'}'>{pct(u['ev'])}</td></tr>" for u in kel["sens_up"])
    m = kel["mid"]
    km = kelly(p, up, dn, m)
    return f"""<section class="card price-top" id="kelly"><h2>Tỷ lệ Kelly — nên dùng bao nhiêu % vốn?</h2>
<p class="sub">Giả định: mua trong vùng {vn(zone[0]) + '–' + vn(zone[1]) if zone else vn(P0)} đ; trong khoảng {N} năm, <b>{vn(p * 100, 0)}%</b> khả năng giá lên <b>{vn(up)} đ</b>, <b>{vn(q * 100, 0)}%</b> khả năng giá xuống <b>{vn(dn)} đ</b>.</p>
<div class="pricebox">
<div><span class="l">Mua giữa vùng {vn(m)} đ</span><span class="v">Kelly {vn(km['f'] * 100, 0)}%</span><span class="l">lãi nếu đúng {pct(km['b'])} · lỗ nếu sai −{vn(km['l'] * 100, 0)}%</span></div>
<div><span class="l">Giá trị kỳ vọng mỗi đồng</span><span class="v {'pos' if km['ev'] > 0 else 'neg'}">{pct(km['ev'])}</span><span class="l">= {vn(p * 100, 0)}% × {pct(km['b'], 0)} − {vn(q * 100, 0)}% × {vn(km['l'] * 100, 0)}%</span></div>
<div><span class="l">½ Kelly (khuyên dùng)</span><span class="v">{vn(min(1, max(0, km['f'] / 2)) * 100, 0)}% vốn</span><span class="l">¼ Kelly: {vn(min(1, max(0, km['f'] / 4)) * 100, 0)}% vốn</span></div>
<div><span class="l">Xác suất hòa vốn</span><span class="v">{vn(km['p0'] * 100, 0)}%</span><span class="l">p thấp hơn mức này thì Kelly = 0, không mua</span></div>
</div>
<div class="tw" style="margin-top:12px"><table><tr><th>Giá mua</th><th>Lãi nếu đúng</th><th>Lỗ nếu sai</th><th>Kỳ vọng</th><th>Kelly đầy đủ</th><th>½ Kelly</th><th>¼ Kelly</th><th>Lãi kép/năm kỳ vọng (½ Kelly, trên tổng vốn)</th><th>p hòa vốn</th></tr>
{''.join(rows)}</table></div>
<div class="callout"><b>Cách đọc:</b> Kelly đầy đủ là % vốn làm tài sản tăng nhanh nhất về dài hạn <i>nếu xác suất {vn(p * 100, 0)}/{vn(q * 100, 0)} là đúng</i>. Kelly &gt; 100% nghĩa là công thức muốn vay thêm — không dùng margin nên trần là 100%. Vì xác suất là ước đoán chủ quan, nhà đầu tư thường dùng <b>½ hoặc ¼ Kelly</b>: tăng trưởng chỉ giảm nhẹ nhưng rủi ro sụt vốn giảm mạnh. Phần vốn không đặt vào cổ phiếu này giữ ở tiền gửi/tài sản khác (chưa tính lãi).</div>
{f'<p class="note">{a.value_notes}</p>' if a.value_notes else ''}
<h2 style="margin-top:18px;font-size:16px">Độ nhạy: Kelly đầy đủ ở giá mua {vn(m)} đ khi đổi xác suất và giá nếu sai</h2>
<div class="tw"><table><tr><th>Xác suất</th>{head}</tr>{srows}</table></div>
<h2 style="margin-top:18px;font-size:16px">Độ nhạy theo giá nếu đúng (xác suất {vn(p * 100, 0)}%, giá sai {vn(dn)} đ, mua {vn(m)} đ)</h2>
<div class="tw"><table><tr><th>Giá nếu đúng</th><th>Kelly đầy đủ</th><th>Kỳ vọng</th></tr>{urows}</table></div>
<p class="note">Kelly ở đây là mô hình 2 kết cục cho cả kỳ {N} năm, chỉ tính giá, chưa tính cổ tức và thuế (cổ tức làm kết quả tốt hơn một chút ở cả hai nhánh). Lãi kép/năm kỳ vọng = e^(tăng trưởng log kỳ vọng ÷ {N}) − 1 trên tổng vốn, khi đặt ½ Kelly. Mô hình giả định giữ đến khi giá chạm một trong hai mức — <b>không có cắt lỗ 7–8%</b>, nên chỉ hợp với chiến lược tích trữ/giữ dài hạn, không dùng cho vị thế CAN SLIM.</p>
<div class="gloss"><div><b>Kelly</b> (công thức Kelly, John Kelly 1956; Ed Thorp áp dụng cho đầu tư): f* = p ÷ (lỗ nếu sai) − (1 − p) ÷ (lãi nếu đúng), với p là xác suất đúng. <b>Kỳ vọng</b>: trung bình lãi/lỗ trên mỗi đồng nếu lặp lại nhiều lần. <b>½ Kelly</b>: dùng một nửa tỷ lệ Kelly để dự phòng ước sai xác suất. <b>p hòa vốn</b>: xác suất tối thiểu để kỳ vọng bằng 0. <b>Margin</b>: vay tiền công ty chứng khoán để mua.</div></div>
</section>
"""


def render(a, css, rows, me, ytabs, taxes, feas, cur_pe, target, s, S5, S10, N5, N10, sh0, P0, kel=None, divsc=None):
    e = html.escape
    sym = e(a.symbol.upper())
    k = 1 if a.add_amount else 0  # có mua thêm: mỗi bảng bán có thêm 1 bảng mua thêm ngay dưới
    o = []
    w = o.append
    w(f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{sym} kế hoạch mua bán</title><style>{css}</style></head><body><div class="wrap">
<header><div class="eyebrow">VNamStock · Kế hoạch mua bán {N5}–{N10} năm</div>
<h1>{sym}{(' · ' + e(a.name)) if a.name else ''}</h1>
<div class="sub">Ngày lập {e(a.date)} · {vn(sh0)} cp{' (minh họa, thay bằng số thật)' if a.planned else ''}, {'giá mua dự kiến' if a.planned else 'giá vốn'} {vn(P0)} đ{(' (vùng mua ' + vn(zone_of(a)[0]) + '–' + vn(zone_of(a)[1]) + ' đ)') if zone_of(a) else ''}{(' · giá thị trường ' + vn(a.market_price) + ' đ ' + e(a.market_date)) if a.market_price else ''} · cổ tức giả định {vn(a.dps)} đ/cp tiền mặt{(' (tăng ' + vn(a.dps_growth, 0) + '%/năm)') if a.dps_growth else ''} + {vn(a.stock_pct, 0 if a.stock_pct == int(a.stock_pct) else 1)}% cổ phiếu mỗi năm, luôn tái đầu tư · giá định bán {vn(S5)} đ sau {N5} năm{'' if S10 == S5 else f', {vn(S10)} đ sau {N10} năm'}</div></header>

<section class="card price-top" id="tomtat"><h2>Tóm tắt kế hoạch</h2>
<div class="pricebox">
<div><span class="l">Vốn bỏ ra</span><span class="v">{tr(sh0 * P0)}</span><span class="l">{vn(sh0)} cp × {vn(P0)} đ</span></div>
<div><span class="l">Bán {vn(S5)} đ sau {N5} năm</span><span class="v">{tr(me['t2']['V'])}</span><span class="l">{pct(me['t2']['tot'])} · {pct(me['t2']['cagr'], 1, False)}/năm</span></div>
<div><span class="l">Bán {vn(S10)} đ sau {N10} năm</span><span class="v">{tr(me['t3']['V'])}</span><span class="l">{pct(me['t3']['tot'])} · {pct(me['t3']['cagr'], 1, False)}/năm</span></div>
<div><span class="l">Còn lại sau thuế, bán năm {N5}</span><span class="v">{tr(taxes[N5]['net'])}</span><span class="l">bán năm {N10}: {tr(taxes[N10]['net'])}</span></div>
</div>
<div class="callout"><b>Điều kiện để kế hoạch đúng:</b> giá không bị giảm hẳn sau mỗi lần chia cổ phiếu, tức lợi nhuận công ty phải tăng ít nhất khoảng {vn(a.stock_pct, 0)}%/năm để vẫn trả {vn(a.dps)} đ trên số cổ phiếu ngày càng nhiều. Tái đầu tư giả định mua lại được ở giá mua ban đầu; nếu giá tăng dần thì số cp mua thêm ít hơn.</div>
{f'<p class="note">Căn cứ giả định cổ tức: {a.div_note}</p>' if a.div_note else ''}
<div class="gloss"><div><b>Lãi kép/năm</b>: mức tăng đều mỗi năm để vốn ban đầu đạt tổng tiền khi bán. <b>Tái đầu tư</b>: dùng tiền cổ tức mua thêm chính cổ phiếu đó. <b>Cổ tức cổ phiếu</b>: công ty trả thêm cổ phiếu thay cho tiền; ngày chia, giá sàn tự điều chỉnh giảm nên tổng giá trị như cũ.</div></div>
</section>

{render_kelly(a, kel, P0, zone_of(a)) if kel else ''}
{render_divsc(a, divsc, P0, S5, S10, N5, N10) if divsc else ''}
<nav>{'<a href="#kelly">Kelly</a>' if kel else ''}{'<a href="#cotuc">Kịch bản cổ tức</a>' if divsc else ''}<a href="#b1">1 · Giữ {N5} năm</a><a href="#b2">2 · Bán sau {N5} năm</a>{f'<a href="#muathem">3 · Mua thêm, {N5} năm</a>' if a.add_amount else ''}<a href="#b3">{3 + k} · Bán sau {N10} năm</a>{f'<a href="#muathem10">5 · Mua thêm, {N10} năm</a>' if a.add_amount else ''}<a href="#b4">{4 + 2 * k} · Giá bán ↔ năm giữ ({N5} năm)</a><a href="#b4b">{5 + 2 * k} · Giá bán ↔ năm giữ ({N10} năm)</a>{'<a href="#khathi">Khả thi</a>' if feas else ''}<a href="#thue">Thuế</a><a href="#thuatngu">Thuật ngữ</a></nav>
""")

    # Mục 1: giá giữ nguyên
    w(f"""<section class="card" id="b1"><h2>1 · Giữ {N5} năm, giá không đổi</h2>
<p class="sub">Giá giữ bằng giá mua; chỉ tính cổ phiếu thưởng và cổ tức tái đầu tư. Bậc giá mua kéo xuống dưới nửa giá thị trường để lên kế hoạch mua thêm.</p>
<div class="tw"><table><tr><th>Giá mua</th>{'<th>So với giá TT</th>' if a.market_price else ''}<th>Vốn</th><th>Số cp sau {N5} năm</th><th>Tổng số tiền</th><th>Tổng tăng</th><th>Lãi kép/năm</th></tr>""")
    for r in rows:
        t = r["t1"]
        vs = f"<td>{pct(r['P'] / a.market_price - 1)}</td>" if a.market_price else ""
        w(f"<tr{trc(r)}><td>{label(r)}</td>{vs}<td>{tr(t['cost'])}</td><td>{vn(t['sh'])}</td><td><b>{tr(t['V'])}</b></td><td><b>{pct(t['tot'])}</b></td><td>~{pct(t['cagr'], 1, False)}</td></tr>")
    w(f"""</table></div>
<div class="gloss"><div><b>Tổng số tiền</b>: số cp sau {N5} năm × giá mua. <b>Tổng tăng</b>: (tổng số tiền − vốn) ÷ vốn. <b>So với giá TT</b>: giá mua cao/thấp hơn giá thị trường hiện tại bao nhiêu %. Số liệu trước thuế.</div></div></section>
""")

    def sell_table(key, n, S, sid, title, add=False):
        sub = f"Mua thêm theo lô {a.lot} cp; chỉ tính phần tiền mới. " if add else ""
        w(f"""<section class="card" id="{sid}"><h2>{title}</h2>
<p class="sub">{sub}Cổ tức tiền mặt luôn tái đầu tư ở giá mua.</p>
<div class="tw"><table><tr><th>Giá mua</th>{'<th>Cp mua thêm</th>' if add else ''}<th>Vốn</th><th>Số cp khi bán</th><th>Tổng tiền khi bán</th><th>Tổng lãi</th><th>Lãi kép/năm</th></tr>""")
        for r in rows:
            if add and not r["add"]:
                continue
            t = r["add"][key] if add else r[key]
            extra = f"<td><b>{vn(r['add']['n'])}</b></td>" if add else ""
            w(f"<tr{trc(r)}><td>{label(r)}</td>{extra}<td>{tr(t['cost'])}</td><td>{vn(t['sh'])}</td><td><b>{tr(t['V'])}</b></td><td>{pct(t['tot'])}</td><td>~{pct(t['cagr'], 1, False)}</td></tr>")
        note = "Tiền lẻ không đủ lô không tính. " if add else ""
        w(f"""</table></div>
<p class="note">{note}Tổng tiền = số cp khi bán × {vn(S)} đ.</p>
<div class="gloss"><div><b>Tổng lãi</b>: (tổng tiền khi bán − vốn) ÷ vốn. <b>Lãi kép/năm</b>: mức tăng đều mỗi năm để đạt tổng tiền đó.{' <b>Lô</b>: lệnh khớp chẵn trên HOSE là bội số 100 cp.' if add else ''} Số liệu trước thuế.</div></div></section>
""")

    add_t = f"Mua thêm {tr(a.add_amount)}" if a.add_amount else ""
    sell_table("t2", N5, S5, "b2", f"2 · Bán sau {N5} năm, giá {vn(S5)} đ")
    if a.add_amount:
        sell_table("t2", N5, S5, "muathem", f"3 · {add_t}, bán sau {N5} năm giá {vn(S5)} đ", add=True)
    sell_table("t3", N10, S10, "b3", f"{3 + k} · Bán sau {N10} năm, giá {vn(S10)} đ")
    if a.add_amount:
        sell_table("t3", N10, S10, "muathem10", f"5 · {add_t}, bán sau {N10} năm giá {vn(S10)} đ", add=True)

    # Giá bán ↔ số năm giữ (mốc 5 năm, rồi mốc 10 năm)
    for i, (yt, sid) in enumerate(zip(ytabs, ("b4", "b4b"))):
        n0, S0, tg, cost = yt["n"], yt["S"], yt["target"], yt["cost"]
        w(f"""<section class="card" id="{sid}"><h2>{4 + 2 * k + i} · Giá bán ↔ số năm giữ, mốc {n0} năm</h2>
<p class="sub">Mốc: giữ <b>{n0} năm</b>, bán <b>{vn(S0)} đ</b>, tổng thu về <b>{tr(tg)}</b>. Số năm cần giữ ở mỗi giá bán để có đúng số tiền đó (theo giá vốn {vn(P0)} đ).</p>
<div class="tw"><table><tr><th>Giá bán</th><th>Số năm giữ tương đương</th><th>So với mốc {n0} năm</th><th>Lãi kép/năm</th></tr>""")
        for x in yt["rows"]:
            cg = f"~{pct((tg / cost) ** (1 / x['years']) - 1, 1, False)}" if x["years"] else "—"
            d = x["diff"]
            if x["sell"] == S0:
                cmp_, cls = "mốc", ' class="me"'
            elif d is None:
                cmp_, cls = "—", ""
            else:
                cmp_ = (f"sớm {ym(-d)}" if d < 0 else f"lâu hơn {ym(d)}")
                cls = ""
            w(f"<tr{cls}><td>{vn(x['sell'])}</td><td><b>{'~' if x['sell'] != S0 else ''}{ym(x['years'])}</b></td><td>{cmp_}</td><td>{cg}</td></tr>")
        w(f"""</table></div>
<p class="note">Mỗi năm giữ thêm, số cp tăng khoảng {pct(s + a.dps / P0, 1, False)} (cổ phiếu thưởng + cổ tức tái đầu tư), bù cho giá bán thấp hơn.</p>
<div class="gloss"><div><b>Số năm giữ tương đương</b>: thời gian cần giữ để số cp × giá bán bằng kịch bản bán {vn(S0)} đ sau {n0} năm. <b>Lãi kép/năm</b>: cùng số tiền {tr(tg)} nhưng đạt sớm hay muộn, tính trên vốn {tr(cost)}. Chưa trừ thuế.</div></div></section>
""")

    if feas:
        w(f"""<section class="card" id="khathi"><h2>Giá bán đó có thực tế không?</h2>
<div class="tw"><table><tr><th>Kịch bản</th><th>Tương đương giá hôm nay</th><th>Vốn hóa khi bán</th><th>LN cần tăng/năm nếu P/E {vn(a.pe_assume, 1)}</th><th>Nếu P/E như hiện tại{f' ({vn(cur_pe, 1)})' if cur_pe else ''}</th></tr>""")
        for f in feas:
            w(f"<tr><td>Bán {vn(f['S'])} đ sau {f['n']} năm</td><td>{vn(f['eq'])} đ</td><td>{vn(f['cap'])} tỷ</td><td><b>{pct(f['g_pe'], 1, False)}</b></td><td>{pct(f['g_cur'], 1, False) if f['g_cur'] is not None else 'N/A'}</td></tr>")
        w(f"""</table></div>
<p class="note">So với LN mẹ 4 quý gần nhất {vn(a.ttm_profit)} tỷ đ và {vn(a.shares_out, 1)} triệu cp lưu hành hiện tại.</p>
<div class="gloss"><div><b>Tương đương giá hôm nay</b>: giá bán × số lần cổ phiếu công ty đã nhân lên do chia thưởng, để so với giá hiện tại. <b>Vốn hóa</b>: giá × tổng số cổ phiếu, tức giá trị cả công ty trên sàn. <b>P/E</b>: giá ÷ lợi nhuận mỗi cổ phiếu. <b>LN mẹ</b>: lợi nhuận thuộc cổ đông công ty mẹ.</div></div></section>
""")

    w(f"""<section class="card" id="thue"><h2>Thuế ước tính với giá vốn</h2>
<div class="tw"><table><tr><th>Kịch bản</th><th>Thuế cổ tức tiền 5%</th><th>Thuế bán 0,1%</th><th>Thuế cp thưởng 5% × mệnh giá</th><th>Tổng thuế</th><th>Còn lại sau thuế</th><th>Lãi sau thuế</th></tr>""")
    for n, S in ((N5, S5), (N10, S10)):
        t = taxes[n]
        w(f"<tr><td>Bán {vn(S)} đ sau {n} năm</td><td>{tr(t['cash'])}</td><td>{tr(t['sale'])}</td><td>{tr(t['bonus'])}</td><td>{tr(t['total'])}</td><td><b>{tr(t['net'])}</b></td><td>{pct(t['net'] / t['cost'] - 1)}</td></tr>")
    w(f"""</table></div>
<div class="gloss"><div><b>Mệnh giá</b>: {vn(PAR)} đ/cp; thuế cổ phiếu thưởng tính 5% trên mệnh giá khi bán. Thuế cổ tức tiền bị trừ trước khi tái đầu tư nên thực tế mua thêm được ít hơn một chút. Mức thuế theo quy định hiện hành, có thể thay đổi.</div></div></section>

<section class="card" id="thuatngu"><h2>Giải thích thuật ngữ</h2><dl class="g">
<dt>Cổ tức tiền mặt</dt><dd>Tiền công ty trả cho mỗi cổ phiếu; % cổ tức ở Việt Nam tính trên mệnh giá {vn(PAR)} đ (20% = 2.000 đ/cp).</dd>
<dt>Cổ tức cổ phiếu</dt><dd>Công ty trả thêm cổ phiếu (10% = 100 cp nhận thêm 10 cp); giá được điều chỉnh giảm nên tự nó không tạo ra tiền.</dd>
<dt>Tái đầu tư</dt><dd>Dùng tiền cổ tức mua thêm chính cổ phiếu đó.</dd>
<dt>Lãi kép</dt><dd>Lãi năm trước được đầu tư tiếp để năm sau sinh thêm lãi.</dd>
<dt>CAGR</dt><dd>Tăng trưởng kép bình quân mỗi năm (Compound Annual Growth Rate).</dd>
</dl></section>
""")
    links = []
    for x in a.sources.split(" | "):
        if not x.strip():
            continue
        t, _, u = x.partition("::")
        links.append(f'<a href="{e(u.strip())}">{e(t.strip())}</a>' if u else e(t.strip()))
    links = " · ".join(links)
    w(f"""<footer>Phép tính minh họa theo giả định đã nêu, không phải tư vấn đầu tư cá nhân. Dữ liệu: {os.path.basename(os.path.splitext(a.out)[0])}.json.{(' Nguồn: ' + links) if links else ''}</footer>
</div></body></html>""")
    return "".join(o)


if __name__ == "__main__":
    main()
