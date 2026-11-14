"""Payback Time theo Phil Town cho báo cáo 4M — dùng chung VNamStock (VND) và USStock (USD).

Nguyên lý (ghi chú của chuyên gia, 11/11/2026): mua cổ phiếu như mua đứt cả công ty.
Cộng dồn dòng tiền tự do (FCF) dự kiến trong 8 năm; nếu tổng ≥ vốn hóa thị trường thì giá hiện tại
là giá Payback Time (mua được), nếu không thì giá đang đắt, nên chờ.

  FCF            = dòng tiền hoạt động (CFO) − capex, năm gần nhất
  g              = số thấp hơn giữa tăng trưởng quá khứ và dự báo nhà phân tích, trần --cap (mặc định 15%)
                   tăng trưởng quá khứ mặc định = thấp hơn giữa tăng BVPS và tăng EPS kỳ dài nhất có dữ liệu
  FCF năm n      = FCF × (1+g)^n, n = 1..8
  Giá Payback    = Σ 8 năm ÷ số cổ phiếu lưu hành
Báo cáo luôn in đủ 3 phần: (1) vì sao chọn g — bảng tăng trưởng 10/5/1 năm của doanh thu, EPS, BVPS,
dòng tiền + ROIC; (2) bốn chỉ số có cùng xác nhận g không; (3) Payback Time từng bước + độ nhạy.

Chuỗi số nhập dạng năm:giá trị, vd 2016:1200,2021:2500,2024:3900,2025:4300 (cần năm cuối, năm cuối−1,
năm cuối−5, năm cuối−10 để có đủ 1/5/10 năm; thiếu năm nào thì ô đó ghi "thiếu dữ liệu").
--fcf/--cfo/--capex/--mcap cùng một đơn vị (--unit, vd "tỷ đ" hoặc "triệu USD"); --unit-mult là số tiền
của 1 đơn vị (tỷ đ = 1e9, triệu USD = 1e6) để quy ra giá mỗi cổ phiếu.

Ví dụ:
  python -I payback_time.py --symbol FPT --currency VND --unit "tỷ đ" --unit-mult 1e9 \
    --cfo 9800 --capex 3600 --fcf-year 2025 --shares 1703000000 --price 50800 \
    --revenue 2015:37960,2020:29830,2024:62849,2025:70113 --eps 2020:2100,2024:4900,2025:5452 \
    --bvps 2020:9800,2024:19500,2025:22736 --cash 2020:6300,2024:9100,2025:9800 \
    --roic 2021:17,2022:18,2023:19,2024:20,2025:21 --analyst 18 --sens 10 \
    --growth-note "VN ít dự báo nên giữ trần 15%" --out <ROOT>/FPT/4M/payback_time
Ngân hàng/bảo hiểm/chứng khoán: thêm --financial (FCF không phù hợp → ghi N/A và lý do).
In JSON + đoạn HTML <section id="paybacktime"> (payback_time.html) để dán vào phần Margin of Safety.
"""
import argparse, json, html, os, sys

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
E = html.escape


def vn(x, d=0):
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, d=1, sign=True):
    if x is None: return "thiếu dữ liệu"
    return (("+" if x > 0 and sign else "") + vn(x * 100, d) + "%").replace("-", "−")


def series(s):
    return dict(sorted((int(a), float(b)) for a, b in (x.split(":") for x in s.split(","))))


def growth(ser, n):
    """Tăng trưởng kép n năm tính tới năm cuối của chuỗi; None nếu thiếu năm hoặc số ≤ 0."""
    if not ser: return None
    last = max(ser); y0 = last - n
    if y0 not in ser or ser[y0] <= 0 or ser[last] <= 0: return None
    return (ser[last] / ser[y0]) ** (1 / n) - 1


def longest(ser):
    """Tăng trưởng kép kỳ dài nhất có dữ liệu (đầu chuỗi → cuối chuỗi) và số năm."""
    if not ser or len(ser) < 2: return None, 0
    y0, y1 = min(ser), max(ser)
    if ser[y0] <= 0 or ser[y1] <= 0: return None, y1 - y0
    return (ser[y1] / ser[y0]) ** (1 / (y1 - y0)) - 1, y1 - y0


def pill(txt, kind):
    return f'<span class="pill p-{kind}">{E(txt)}</span>'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", required=True); ap.add_argument("--currency", default="VND", choices=["USD", "VND"])
    ap.add_argument("--unit", default="tỷ đ", help='đơn vị của FCF/vốn hóa, vd "tỷ đ", "triệu USD"')
    ap.add_argument("--unit-mult", type=float, default=1e9, help="1 đơn vị = bao nhiêu đồng/USD")
    ap.add_argument("--fcf", type=float, help="FCF năm gần nhất (nếu không truyền thì = cfo − capex)")
    ap.add_argument("--cfo", type=float, help="dòng tiền hoạt động năm gần nhất")
    ap.add_argument("--capex", type=float, help="chi đầu tư TSCĐ năm gần nhất (số dương)")
    ap.add_argument("--fcf-year", default="", help="năm/kỳ của FCF, vd 2025 hoặc 'TTM Q3/2026'")
    ap.add_argument("--fcf-note", default="", help="ghi chú nếu FCF được chuẩn hóa")
    ap.add_argument("--shares", type=float, required=True, help="số cổ phiếu lưu hành (số tuyệt đối)")
    ap.add_argument("--price", type=float, required=True, help="giá tham chiếu mỗi cổ phiếu")
    ap.add_argument("--price-date", default="")
    ap.add_argument("--mcap", type=float, help="vốn hóa theo --unit (mặc định = giá × số cp)")
    for k, h in (("revenue", "doanh thu"), ("eps", "EPS"), ("bvps", "BVPS/vốn chủ sở hữu"), ("cash", "dòng tiền (CFO hoặc FCF)")):
        ap.add_argument("--" + k, help=f"chuỗi {h} theo năm, năm:giá trị,…")
    ap.add_argument("--roic", help="ROIC %% theo năm, năm:giá trị,…")
    ap.add_argument("--analyst", type=float, help="dự báo tăng trưởng của nhà phân tích, %%/năm")
    ap.add_argument("--analyst-src", default="", help="nguồn dự báo")
    ap.add_argument("--growth", type=float, help="ghi đè g %% (bắt buộc nêu lý do trong --growth-note)")
    ap.add_argument("--growth-note", default="", help="lý do hạ g thêm: công ty lớn, ngành chu kỳ, thiếu dữ liệu…")
    ap.add_argument("--cap", type=float, default=15.0, help="trần g dài hạn %%, mặc định 15 (không vượt 20)")
    ap.add_argument("--floor", type=float, default=10.0, help="mức tăng trưởng mong muốn %%/năm")
    ap.add_argument("--sens", default="10", help="các mức g thấp hơn để kiểm tra độ nhạy, vd 10,8")
    ap.add_argument("--years", type=int, default=8)
    ap.add_argument("--hist-years", default="5,4", help="kỳ ưu tiên để lấy tăng trưởng trung bình lịch sử (năm), vd 5,4; thiếu thì dùng kỳ dài nhất có dữ liệu")
    ap.add_argument("--now-scenarios", default="", help='kịch bản g cố định cho phần "hoàn vốn tại giá hiện tại": "Nhãn|g%%|ghi chú;Nhãn|g%%|ghi chú"')
    ap.add_argument("--fade", default="", help='g hợp lý dạng giảm/tăng dần theo năm: "Nhãn|g1,g2,g3,...|lý do" (số cuối dùng cho các năm sau); đây là kịch bản được chọn')
    ap.add_argument("--now-cap", type=int, default=40, help="số năm tối đa khi dò hoàn vốn")
    ap.add_argument("--financial", action="store_true", help="ngân hàng/bảo hiểm/chứng khoán: FCF không phù hợp")
    ap.add_argument("--financial-note", default="", help="chỉ tiêu thay thế đã dùng cho nhóm tài chính")
    ap.add_argument("--out", required=True, help="đường dẫn không đuôi; ghi .json và .html")
    a = ap.parse_args()

    cur = "đ" if a.currency == "VND" else "$"
    pd_ = 0 if a.currency == "VND" else 2
    def money(x): return (vn(x, pd_) + " đ") if a.currency == "VND" else ("$" + vn(x, pd_))
    floor = a.floor / 100
    mcap = a.mcap if a.mcap is not None else a.price * a.shares / a.unit_mult
    out_base = os.path.splitext(a.out)[0]
    os.makedirs(os.path.dirname(os.path.abspath(out_base)) or ".", exist_ok=True)
    res = dict(symbol=a.symbol, currency=a.currency, unit=a.unit, price=a.price, shares=a.shares, mcap=mcap)
    H = [f'<section class="card" id="paybacktime"><h2>Payback Time (Phil Town) — bao lâu thì hoàn vốn ở giá hiện tại</h2>',
         f'<p class="sub">Coi như mua đứt cả công ty ở giá hôm nay: cộng dồn dòng tiền tự do (FCF) dự kiến từng năm cho tới khi bằng vốn hóa thị trường — số năm đó là thời gian hoàn vốn. '
         f'Mốc của Phil Town: hoàn vốn trong {a.years} năm trở xuống là giá mua được; lâu hơn là giá đang đắt, nên chờ. Chạy song song với Sticker Price / giá MOS, không lấy trung bình.</p>']

    # ---------- nhóm tài chính: không áp dụng ----------
    if a.financial:
        note = a.financial_note or "dùng chỉ tiêu khác trong phần định giá (P/B, ROE, lợi nhuận thặng dư) thay cho FCF."
        H.append(f'<div class="callout"><b>Không áp dụng (N/A):</b> với ngân hàng, bảo hiểm, chứng khoán, tiền gửi và nợ là nguyên liệu kinh doanh nên '
                 f'FCF (dòng tiền hoạt động trừ capex) không phản ánh tiền thuộc về cổ đông. {E(note)}</div>')
        H.append('<div class="gloss"><div><b>FCF</b> (dòng tiền tự do): tiền thu từ hoạt động kinh doanh trừ tiền đầu tư tài sản cố định. '
                 '<b>N/A</b>: không áp dụng.</div></div></section>')
        res.update(applicable=False, reason="financial")
        _write(out_base, res, H); return

    # ---------- phần 1: vì sao chọn g ----------
    ser = {k: (series(getattr(a, k)) if getattr(a, k) else {}) for k in ("revenue", "eps", "bvps", "cash")}
    names = dict(revenue="Doanh thu", eps="EPS", bvps="Vốn chủ sở hữu (BVPS)", cash="Dòng tiền")
    tbl = {}
    for k, s in ser.items():
        g10, g5, g1 = growth(s, 10), growth(s, 5), growth(s, 1)
        gl, nl = longest(s)
        have = [x for x in (g10, g5, g1) if x is not None]
        if not have: reach, stab = "Thiếu dữ liệu", "Thiếu dữ liệu"
        else:
            reach = "Đạt" if all(x >= floor for x in have) else ("Một phần" if any(x >= floor for x in have) else "Không đạt")
            stab = "Thất thường" if any(x < 0 for x in have) else ("Ổn định" if all(x >= floor for x in have) else "Dao động")
        tbl[k] = dict(g10=g10, g5=g5, g1=g1, longest=gl, longest_years=nl, reach=reach, stability=stab)
    roic = series(a.roic) if a.roic else {}
    roic_avg = sum(roic.values()) / len(roic) if roic else None
    roic_ok = (min(roic.values()) >= a.floor) if roic else None

    hist_c = {k: tbl[k]["longest"] for k in ("bvps", "eps") if tbl[k]["longest"] is not None}
    hist = min(hist_c.values()) if hist_c else None
    hist_from = min(hist_c, key=hist_c.get) if hist_c else None
    analyst = a.analyst / 100 if a.analyst is not None else None
    cands = [x for x in (hist, analyst) if x is not None]
    steps = []
    if a.growth is not None:
        g = a.growth / 100; how = f"g đặt tay {pct(g, 1, False)}"
        steps.append(f"g được đặt tay ở {pct(g, 1, False)}. Lý do: {E(a.growth_note) or '<b>CHƯA NÊU LÝ DO — phải bổ sung --growth-note</b>'}.")
    elif not cands:
        print("Thiếu dữ liệu để chọn g: cần --bvps/--eps hoặc --analyst hoặc --growth", file=sys.stderr); sys.exit(2)
    else:
        raw = min(cands); g = min(raw, a.cap / 100)
        if hist is not None:
            steps.append(f"Tăng trưởng quá khứ: {pct(hist, 1, False)}/năm — số thấp hơn giữa tăng BVPS và tăng EPS, kỳ dài nhất có dữ liệu "
                         f"({names[hist_from]}, {tbl[hist_from]['longest_years']} năm).")
        else:
            steps.append("Tăng trưởng quá khứ: thiếu dữ liệu BVPS/EPS.")
        if analyst is not None:
            steps.append(f"Dự báo của nhà phân tích: {pct(analyst, 1, False)}/năm{(' (' + E(a.analyst_src) + ')') if a.analyst_src else ''}.")
        else:
            steps.append("Dự báo của nhà phân tích: không có — chỉ dựa vào tăng trưởng quá khứ, nên càng phải thận trọng.")
        steps.append(f"Lấy con số thấp hơn: {pct(raw, 1, False)}.")
        if raw > a.cap / 100:
            steps.append(f"Vượt trần dài hạn {vn(a.cap, 0)}% nên hạ về {pct(g, 1, False)} (dài hạn không dùng trên 15–20%).")
        if a.growth_note: steps.append(f"Ghi chú thêm: {E(a.growth_note)}.")
        how = "thấp hơn giữa quá khứ và dự báo" + (", chạm trần" if raw > a.cap / 100 else "")
    if g <= 0:
        steps.append("<b>g ≤ 0:</b> doanh nghiệp không tăng trưởng theo số liệu đã chọn — Payback Time chỉ còn ý nghĩa tham khảo.")

    def cell(x):
        if x is None: return '<td class="l" style="text-align:right">thiếu dữ liệu</td>'
        return f'<td class="{"pos" if x >= floor else "neg"}">{pct(x)}</td>'
    def tag(t):
        kind = {"Đạt": "good", "Ổn định": "good", "Một phần": "warn", "Dao động": "warn"}.get(t, "bad")
        return pill(t, kind)
    H.append(f'<h3>1. Vì sao chọn tốc độ tăng trưởng g = {pct(g, 1, False)}/năm</h3>')
    H.append('<div class="tw"><table><thead><tr><th>Chỉ số</th><th>10 năm</th><th>5 năm</th><th>1 năm</th>'
             f'<th>Đạt ~{vn(a.floor, 0)}%/năm?</th><th>Ổn định?</th></tr></thead><tbody>')
    for k in ("revenue", "eps", "bvps", "cash"):
        t = tbl[k]
        H.append(f'<tr><td>{names[k]}</td>{cell(t["g10"])}{cell(t["g5"])}{cell(t["g1"])}<td>{tag(t["reach"])}</td><td>{tag(t["stability"])}</td></tr>')
    if roic:
        rr = " · ".join(f"{y}: {vn(v, 1)}%" for y, v in roic.items())
        H.append(f'<tr><td>ROIC</td><td colspan="3" class="l" style="text-align:right">{rr}</td>'
                 f'<td>{tag("Đạt" if roic_ok else "Không đạt")}</td><td>TB {vn(roic_avg, 1)}%</td></tr>')
    else:
        H.append('<tr><td>ROIC</td><td colspan="3" class="l" style="text-align:right">thiếu dữ liệu</td><td>—</td><td>—</td></tr>')
    H.append('</tbody></table></div>')
    H.append('<ul>' + ''.join(f'<li>{s}</li>' for s in steps) + '</ul>')

    # ---------- phần 2: bốn chỉ số có xác nhận g không ----------
    conf, off = [], []
    for k in ("revenue", "eps", "bvps", "cash"):
        gl = tbl[k]["longest"]
        if gl is None: st = "Thiếu dữ liệu"
        elif gl >= g: st = "Xác nhận"
        elif gl >= g - 0.05: st = "Thấp hơn một chút"
        else: st = "Lệch nhiều"
        tbl[k]["confirm"] = st
        (conf if st == "Xác nhận" else off).append((k, st, gl))
    n_ok = len(conf)
    verdict = ("Cả bốn chỉ số cùng xác nhận" if n_ok == 4 else f"{n_ok}/4 chỉ số xác nhận") + f" mức g = {pct(g, 1, False)}."
    H.append('<h3>2. Bốn chỉ số có cùng xác nhận g không</h3>')
    H.append('<div class="tw"><table><thead><tr><th>Chỉ số</th><th>Tăng trưởng kỳ dài nhất</th><th>Số năm</th><th>So với g đã chọn</th></tr></thead><tbody>')
    for k in ("revenue", "eps", "bvps", "cash"):
        t = tbl[k]; kind = {"Xác nhận": "good", "Thấp hơn một chút": "warn"}.get(t["confirm"], "bad")
        H.append(f'<tr><td>{names[k]}</td><td>{pct(t["longest"])}</td><td>{t["longest_years"] or "—"}</td><td>{pill(t["confirm"], kind)}</td></tr>')
    H.append('</tbody></table></div>')
    msg = f'<b>Kết luận:</b> {verdict}'
    if off:
        msg += ' Chỉ số chưa xác nhận: ' + '; '.join(
            f'{names[k]} ({st.lower()}{", " + pct(gl) if gl is not None else ""})' for k, st, gl in off) + \
            '. Chỉ số lệch nhiều nghĩa là g có thể đang cao so với thực tế của chỉ số đó — xem dòng độ nhạy bên dưới và giải thích nguyên nhân trong báo cáo.'
    H.append(f'<div class="callout">{msg}</div>')

    # ---------- phần 3: Payback Time từng bước ----------
    fcf = a.fcf if a.fcf is not None else ((a.cfo - a.capex) if (a.cfo is not None and a.capex is not None) else None)
    if fcf is None:
        print("Thiếu FCF: truyền --fcf hoặc cả --cfo và --capex", file=sys.stderr); sys.exit(2)
    H.append('<h3>3. Payback Time từng bước</h3>')
    yr = f" {E(a.fcf_year)}" if a.fcf_year else " năm gần nhất"
    if a.cfo is not None and a.capex is not None:
        H.append(f'<p><b>Bước 1 — FCF{yr}:</b> dòng tiền hoạt động {vn(a.cfo, 1)} − capex {vn(a.capex, 1)} = <b>{vn(fcf, 1)} {E(a.unit)}</b>.'
                 f'{(" " + E(a.fcf_note)) if a.fcf_note else ""}</p>')
    else:
        H.append(f'<p><b>Bước 1 — FCF{yr}:</b> <b>{vn(fcf, 1)} {E(a.unit)}</b> (dòng tiền hoạt động trừ capex).{(" " + E(a.fcf_note)) if a.fcf_note else ""}</p>')
    res.update(fcf=fcf, g=g, how=how, growth_table=tbl, roic=roic, confirm=verdict)
    if fcf <= 0:
        H.append('<div class="callout"><b>Không tính được (N/A):</b> FCF âm hoặc bằng 0 nên không có dòng tiền để hoàn vốn. '
                 'Nêu lý do FCF âm (đầu tư mở rộng, vốn lưu động, chu kỳ…) và dùng các phương pháp khác trong phần Margin of Safety.</div></section>')
        res.update(applicable=False, reason="fcf<=0")
        _write(out_base, res, H); return

    # ---------- hoàn vốn tại giá hiện tại (yêu cầu 13/11/2026): g = trung bình lịch sử 5/4 năm, rồi g điều chỉnh hợp lý ----------
    def years_to_payback(path):
        """path: list g theo năm (số cuối lặp lại). Trả (số năm lẻ hoặc None, bảng từng năm)."""
        v, cum, rows = fcf, 0.0, []
        for n in range(1, a.now_cap + 1):
            gg = path[min(n - 1, len(path) - 1)]
            v *= 1 + gg; prev = cum; cum += v
            rows.append(dict(n=n, g=gg, fcf=v, cum=cum))
            if cum >= mcap:
                return (n - 1 + (mcap - prev) / v if v > 0 else None), rows
            if v <= 0: break
        return None, rows
    hist_pref = [int(x) for x in a.hist_years.split(",") if x.strip()]
    hist_used = {}
    for k in ("revenue", "eps", "bvps", "cash"):
        sk = ser[k]; got = None
        for n in hist_pref:
            gv = growth(sk, n)
            if gv is not None: got = (gv, n); break
        if got is None and tbl[k]["longest"] is not None: got = (tbl[k]["longest"], tbl[k]["longest_years"])
        if got: hist_used[k] = got
    scen = []
    if hist_used:
        havg = sum(v for v, _ in hist_used.values()) / len(hist_used)
        yrs = sorted({n for _, n in hist_used.values()})
        det = "; ".join(f"{names[k]} {pct(v, 1)} ({n} năm)" for k, (v, n) in hist_used.items())
        scen.append(dict(label=f"Trung bình tăng trưởng lịch sử ({'/'.join(str(y) for y in yrs)} năm)", path=[havg], kind="hist",
                         note=f"Trung bình tăng trưởng kép của {len(hist_used)} chỉ số: {det}." + ("" if max(yrs) >= 4 else " Nguồn dữ liệu chỉ có " + str(max(yrs)) + " năm tăng trưởng, chưa đủ 4–5 năm.")))
    for item in [x for x in a.now_scenarios.split(";") if x.strip()]:
        parts = [x.strip() for x in item.split("|")]
        scen.append(dict(label=parts[0], path=[float(parts[1]) / 100], kind="const", note=parts[2] if len(parts) > 2 else ""))
    chosen = None
    if a.fade:
        parts = [x.strip() for x in a.fade.split("|")]
        chosen = dict(label=parts[0], path=[float(x) / 100 for x in parts[1].split(",")], kind="chosen", note=parts[2] if len(parts) > 2 else "")
        scen.append(chosen)
    scen.append(dict(label=f"Trần dài hạn của Phil Town ({pct(g, 1, False)})", path=[g], kind="cap", note="Mức g dùng cho phép thử 8 năm bên dưới."))
    for sc in scen: sc["years"], sc["rows"] = years_to_payback(sc["path"])
    # g cố định cần có để hoàn vốn đúng a.years năm ở giá hiện tại
    lo, hi = -0.5, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2
        tot = sum(fcf * (1 + mid) ** n for n in range(1, a.years + 1))
        lo, hi = (mid, hi) if tot < mcap else (lo, mid)
    g_need = hi
    def ytxt(y): return f"{vn(y, 1)} năm" if y is not None else f"&gt; {a.now_cap} năm"
    def gtxt(path): return pct(path[0], 1, False) if len(path) == 1 else " → ".join(vn(x * 100, 0) + "%" for x in path) + " (các năm sau giữ mức cuối)"
    H.append(f'<p><b>Bước 2 — Số năm hoàn vốn tại giá hiện tại:</b> vốn hóa = {money(a.price)} × {vn(a.shares, 0)} cp = <b>{vn(mcap, 1)} {E(a.unit)}</b>'
             f'{(" (" + E(a.price_date) + ")") if a.price_date else ""}. Mỗi năm FCF tăng theo g, cộng dồn tới khi đủ vốn hóa.</p>')
    H.append('<div class="tw"><table><thead><tr><th>Kịch bản tăng trưởng</th><th>g mỗi năm</th><th>Hoàn vốn sau</th>'
             f'<th>So với mốc {a.years} năm</th><th>Ghi chú</th></tr></thead><tbody>')
    for sc in scen:
        okk = sc["years"] is not None and sc["years"] <= a.years
        trc = ' class="chg"' if sc["kind"] == "chosen" else ''
        tagc = " — <b>g hợp lý (đã chọn)</b>" if sc["kind"] == "chosen" else ""
        pl = pill("Trong " + str(a.years) + " năm", "good") if okk else pill("Lâu hơn " + str(a.years) + " năm", "bad")
        H.append(f'<tr{trc}><td class="l"><b>{E(sc["label"])}</b>{tagc}</td><td class="l">{gtxt(sc["path"])}</td>'
                 f'<td><b>{ytxt(sc["years"])}</b></td><td>{pl}</td><td class="l">{E(sc["note"])}</td></tr>')
    H.append('</tbody></table></div>')
    H.append(f'<p class="note">Để hoàn vốn đúng {a.years} năm ở giá hiện tại, FCF phải tăng đều khoảng <b>{pct(g_need, 1, False)}/năm</b> suốt {a.years} năm. '
             'Trung bình lịch sử là phép tính theo yêu cầu: tăng trưởng quá khứ rất cao thường không kéo dài được nhiều năm, nên kết luận dựa trên dòng "g hợp lý".</p>')
    main_now = chosen or next((x for x in scen if x["kind"] == "hist"), scen[0])
    H.append(f'<p><b>Bước 3 — Từng năm với {E(main_now["label"])}:</b></p>')
    H.append(f'<div class="tw"><table><thead><tr><th>Năm</th><th>g năm đó</th><th>FCF ({E(a.unit)})</th><th>Cộng dồn ({E(a.unit)})</th><th>% vốn hóa đã thu về</th></tr></thead><tbody>')
    for r in main_now["rows"]:
        last = r is main_now["rows"][-1] and main_now["years"] is not None
        trc = ' class="chg"' if last else ''
        H.append(f'<tr{trc}><td>{r["n"]}</td><td>{pct(r["g"], 1, False)}</td><td>{vn(r["fcf"], 1)}</td><td><b>{vn(r["cum"], 1)}</b></td><td>{vn(r["cum"] / mcap * 100, 1)}%</td></tr>')
    H.append('</tbody></table></div>')
    yn = main_now["years"]
    okn = yn is not None and yn <= a.years
    box_hist = (f'<div><span class="l">Theo g trung bình lịch sử</span><span class="v">{ytxt(scen[0]["years"])}</span></div>' if scen[0]["kind"] == "hist" else '')
    H.append('<div class="pricebox">'
             f'<div><span class="l">Hoàn vốn tại giá hiện tại (g hợp lý)</span><span class="v">{ytxt(yn)}</span></div>' + box_hist +
             f'<div><span class="l">g cần để hoàn vốn trong {a.years} năm</span><span class="v">{pct(g_need, 1, False)}</span></div></div>')
    head = pill("Hoàn vốn trong " + str(a.years) + " năm", "good") if okn else pill("Hoàn vốn lâu hơn " + str(a.years) + " năm", "bad")
    tail = (f' — đạt mốc {a.years} năm của Phil Town. Vẫn phải đủ 4M và timing mới xét mua.' if okn
            else f' — chậm hơn mốc {a.years} năm của Phil Town; theo Payback Time giá còn đắt, nên chờ.')
    H.append(f'<div class="callout">{head} Với g hợp lý, mua ở giá hiện tại thì khoảng <b>{ytxt(yn)}</b> dòng tiền mới hoàn lại vốn hóa{tail}</div>')
    res["payback_now"] = dict(scenarios=[dict(label=x["label"], kind=x["kind"], path=x["path"], years=x["years"], note=x["note"]) for x in scen],
                              chosen=main_now["label"], chosen_years=yn, hist_years=(scen[0]["years"] if scen[0]["kind"] == "hist" else None),
                              hist_g=(scen[0]["path"][0] if scen[0]["kind"] == "hist" else None),
                              g_needed_for_years=g_need, within=okn, chosen_rows=main_now["rows"])
    H.append(f'<h3>4. Tham chiếu — phép thử {a.years} năm với g trần {pct(g, 1, False)}</h3>')

    def run(gg):
        rows, cum = [], 0.0
        for n in range(1, a.years + 1):
            v = fcf * (1 + gg) ** n; cum += v
            rows.append(dict(n=n, fcf=v, cum=cum))
        per = cum * a.unit_mult / a.shares
        hit = next((r["n"] for r in rows if r["cum"] >= mcap), None)
        return dict(g=gg, rows=rows, total=cum, per_share=per, vs_price=a.price / per - 1, payback_year=hit)
    main_ = run(g)
    H.append(f'<p><b>Dự phóng {a.years} năm với g = {pct(g, 1, False)}:</b></p>')
    H.append(f'<div class="tw"><table><thead><tr><th>Năm</th><th>Phép tính</th><th>FCF ({E(a.unit)})</th><th>Cộng dồn ({E(a.unit)})</th></tr></thead><tbody>')
    for r in main_["rows"]:
        mark = ' class="chg"' if main_["payback_year"] == r["n"] else ''
        H.append(f'<tr{mark}><td>{r["n"]}</td><td>{vn(fcf, 1)} × (1 + {vn(g, 3)})^{r["n"]}</td><td>{vn(r["fcf"], 1)}</td><td><b>{vn(r["cum"], 1)}</b></td></tr>')
    H.append('</tbody></table></div>')
    ok = main_["total"] >= mcap
    diff = main_["vs_price"]
    H.append(f'<p><b>So với vốn hóa:</b> tổng {a.years} năm = <b>{vn(main_["total"], 1)} {E(a.unit)}</b>; vốn hóa = {vn(mcap, 1)} {E(a.unit)} '
             f'({money(a.price)} × {vn(a.shares, 0)} cp{(", " + E(a.price_date)) if a.price_date else ""}). '
             f'Giá Payback Time mỗi cổ phiếu = {vn(main_["total"], 1)} {E(a.unit)} ÷ {vn(a.shares, 0)} cp = <b>{money(main_["per_share"])}</b>.</p>')
    hit = main_["payback_year"]
    H.append('<div class="pricebox">'
             f'<div><span class="l">Giá Payback Time ({a.years} năm)</span><span class="v">{money(main_["per_share"])}</span></div>'
             f'<div><span class="l">Giá hiện tại</span><span class="v">{money(a.price)}</span><span class="l">{pct(diff)} so với giá Payback</span></div>'
             f'<div><span class="l">Hoàn vốn sau</span><span class="v">{(str(hit) + " năm") if hit else ("> " + str(a.years) + " năm")}</span></div></div>')
    if ok:
        H.append(f'<div class="callout">{pill("Dưới giá Payback Time", "good")} Giá hiện tại thấp hơn giá Payback Time {pct(abs(diff), 1, False)} '
                 f'— dòng tiền {a.years} năm đủ hoàn lại toàn bộ vốn hóa. Vẫn phải đủ 4M và timing mới xét mua.</div>')
    else:
        H.append(f'<div class="callout">{pill("Trên giá Payback Time", "bad")} Giá hiện tại cao hơn giá Payback Time {pct(abs(diff), 1, False)} '
                 f'— dòng tiền {a.years} năm chưa đủ hoàn vốn; theo Payback Time giá đang đắt, nên chờ.</div>')

    sens = []
    for s in [float(x) for x in a.sens.split(",") if x.strip()]:
        if abs(s / 100 - g) > 1e-9: sens.append(run(s / 100))
    if sens:
        H.append('<p><b>Kiểm tra độ nhạy với g thấp hơn:</b></p>')
        H.append(f'<div class="tw"><table><thead><tr><th>g</th><th>Tổng {a.years} năm ({E(a.unit)})</th><th>Giá Payback / cp</th><th>Giá hiện tại so với giá Payback</th><th>Kết luận</th></tr></thead><tbody>')
        for r in [main_] + sens:
            good = r["total"] >= mcap
            trc = ' class="chg"' if r is main_ else ''
            H.append(f'<tr{trc}><td>{pct(r["g"], 1, False)}{" (đã chọn)" if r is main_ else ""}</td><td>{vn(r["total"], 1)}</td>'
                     f'<td><b>{money(r["per_share"])}</b></td><td>{pct(r["vs_price"])}</td><td>{pill("Dưới giá Payback" if good else "Trên giá Payback", "good" if good else "bad")}</td></tr>')
        H.append('</tbody></table></div>')
        allgood = all(r["total"] >= mcap for r in sens)
        H.append('<p class="note">' + ("Với g thấp hơn giá vẫn dưới mức Payback Time → biên an toàn tốt." if (ok and allgood) else
                 "Kết luận đổi hoặc không đạt khi hạ g → biên an toàn mỏng, phụ thuộc nhiều vào giả định tăng trưởng.") + '</p>')
    H.append('<div class="gloss">'
             '<div><b>Payback Time</b>: số năm để dòng tiền công ty làm ra hoàn lại số tiền bỏ ra mua cả công ty; Phil Town lấy mốc 8 năm.</div>'
             '<div><b>FCF</b> (dòng tiền tự do): tiền thu từ hoạt động kinh doanh trừ tiền đầu tư tài sản cố định (capex). '
             '<b>Vốn hóa</b>: giá cổ phiếu × số cổ phiếu lưu hành. <b>g</b>: tốc độ tăng trưởng giả định mỗi năm.</div>'
             '<div><b>EPS</b>: lợi nhuận mỗi cổ phiếu. <b>BVPS</b>: giá trị sổ sách (vốn chủ sở hữu) mỗi cổ phiếu. '
             '<b>ROIC</b>: lợi nhuận trên vốn đầu tư. <b>Độ nhạy</b>: tính lại với giả định thấp hơn để xem kết luận có còn đúng.</div>'
             '<div>Đây là một phép thử định giá, không phải cam kết thời gian hồi vốn hay lời khuyên mua bán.</div></div></section>')
    res.update(applicable=True, total=main_["total"], per_share=main_["per_share"], vs_price=diff,
               below_payback=ok, payback_year=hit, rows=main_["rows"],
               sensitivity=[dict(g=r["g"], total=r["total"], per_share=r["per_share"], vs_price=r["vs_price"]) for r in sens])
    _write(out_base, res, H)


def _write(base, res, H):
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(base + ".html", "w", encoding="utf-8") as f:
        f.write("\n".join(H))
    print(json.dumps({k: res.get(k) for k in ("symbol", "applicable", "g", "how", "fcf", "total", "mcap", "per_share", "vs_price", "below_payback", "payback_year", "confirm")}, ensure_ascii=False))
    if res.get("payback_now"):
        pn = res["payback_now"]
        print(json.dumps(dict(now=[(x["label"], x["years"]) for x in pn["scenarios"]], chosen=pn["chosen"], g_needed=pn["g_needed_for_years"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
