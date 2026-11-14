"""Sticker Price theo Phil Town (Rule #1) cho báo cáo 4M — dùng chung VNamStock (VND) và USStock (USD).

Công thức:
  g        = min(tăng BVPS lịch sử, dự báo nhà phân tích nếu có, tăng EPS lịch sử nếu truyền), giới hạn --cap (mặc định 15%)
  P/E 10y  = min(2 × g×100, P/E trung bình lịch sử), tối đa 50
  EPS 10y  = EPS × (1+g)^10
  Giá 10y  = EPS 10y × P/E 10y
  Sticker  = Giá 10y ÷ (1+MARR)^10      (MARR mặc định 15%)
  Giá MOS  = Sticker × (1 − MOS)        (mặc định MOS 50%)
Thêm bảng độ nhạy theo các mức tăng trưởng --sens.

Ví dụ:
  python -I sticker_price.py --symbol GOOGL --currency USD --eps 10.57 --eps-note "EPS chuẩn hóa TTM" \
    --bvps 2022:19.93,2025:34.35 --eps-hist 2022:5.07,2025:9.27 --pe-hist 19.3,24.1,23.5,29.0 \
    --price 288.93 --sens 6,12,15,19.9 --out <ROOT>/GOOGL/4M/sticker.json
In JSON + đoạn HTML <section id="sticker"> (file .html cùng tên) để dán vào báo cáo 4M.
"""
import argparse, json, html, sys

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def series(s):
    pts = sorted((int(a), float(b)) for a, b in (x.split(":") for x in s.split(",")))
    return pts


def cagr(pts):
    (y0, v0), (y1, v1) = pts[0], pts[-1]
    if v0 <= 0 or v1 <= 0 or y1 <= y0: return None
    return (v1 / v0) ** (1 / (y1 - y0)) - 1


def calc(eps, g, pe_hist, marr, mos, years=10):
    pe = min(2 * g * 100, pe_hist if pe_hist else 2 * g * 100, 50)
    fe = eps * (1 + g) ** years; fp = fe * pe; st = fp / (1 + marr) ** years
    return dict(g=g, pe=pe, eps_f=fe, price_f=fp, sticker=st, mos_price=st * (1 - mos))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True); ap.add_argument("--currency", default="USD", choices=["USD", "VND"])
    ap.add_argument("--eps", type=float, required=True, help="EPS 12 tháng gần nhất (chuẩn hóa nếu có khoản bất thường lớn)")
    ap.add_argument("--eps-note", default="")
    ap.add_argument("--bvps", help="BVPS theo năm, vd 2021:19.9,2025:34.4 (lấy năm đầu và cuối)")
    ap.add_argument("--eps-hist", help="EPS theo năm để tính tăng trưởng EPS lịch sử")
    ap.add_argument("--analyst", type=float, help="dự báo tăng EPS 5 năm của nhà phân tích, %%")
    ap.add_argument("--growth", type=float, help="ghi đè tăng trưởng %% (ghi lý do trong --growth-note)")
    ap.add_argument("--growth-note", default="")
    ap.add_argument("--cap", type=float, default=15.0, help="trần tăng trưởng %%, mặc định 15")
    ap.add_argument("--pe-hist", help="danh sách P/E cuối năm lịch sử, vd 19.3,24.1,23.5,29")
    ap.add_argument("--marr", type=float, default=15.0); ap.add_argument("--mos", type=float, default=50.0)
    ap.add_argument("--price", type=float, help="giá tham chiếu"); ap.add_argument("--price-date", default="")
    ap.add_argument("--sens", default="6,12,15", help="các mức tăng trưởng %% cho bảng độ nhạy")
    ap.add_argument("--mos-levels", default="20,30,40,50", help="các bậc biên an toàn %% cho bảng giá mua; tối đa 50 (mức mua chuẩn của Phil Town)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.eps <= 0:
        sys.exit("EPS <= 0: Sticker Price không có ý nghĩa — ghi N/A trong báo cáo.")
    cands = {}
    if a.bvps: cands["Tăng BVPS lịch sử"] = cagr(series(a.bvps))
    if a.eps_hist: cands["Tăng EPS lịch sử"] = cagr(series(a.eps_hist))
    if a.analyst is not None: cands["Dự báo nhà phân tích"] = a.analyst / 100
    valid = {k: v for k, v in cands.items() if v is not None and v > 0}
    neg = {k: v for k, v in cands.items() if v is not None and v <= 0}
    if neg and a.growth is None:
        sys.exit("Tăng trưởng lịch sử âm (" + "; ".join(f"{k} {v:.1%}" for k, v in neg.items()) +
                 "): không đạt điều kiện Rule #1, Sticker Price N/A. Chỉ tính minh họa khi truyền --growth kèm lý do.")
    if a.growth is not None:
        g, how = a.growth / 100, "ghi đè: " + a.growth_note
    elif valid:
        k = min(valid, key=valid.get); g = min(valid[k], a.cap / 100)
        how = f"thấp nhất là {k} {vn(valid[k] * 100, 1)}%" + (f", giới hạn ở {vn(a.cap, 0)}%" if valid[k] > a.cap / 100 else "")
    else:
        sys.exit("Thiếu dữ liệu tăng trưởng (--bvps/--eps-hist/--analyst/--growth).")
    pe_hist = sum(float(x) for x in a.pe_hist.split(",")) / len(a.pe_hist.split(",")) if a.pe_hist else None
    marr, mos = a.marr / 100, a.mos / 100
    main_ = calc(a.eps, g, pe_hist, marr, mos)
    sens = [calc(a.eps, float(x) / 100, pe_hist, marr, mos) for x in a.sens.split(",")]
    # bậc biên an toàn (MOS): mặc định 20/30/40/50%, không vượt 50% (mức mua chuẩn của Phil Town; quy tắc người dùng 13/11/2026, đã sửa từ 60–80)
    MOS_MAX = 50.0
    levels = sorted({min(float(x), MOS_MAX) for x in a.mos_levels.split(",") if x.strip()} | {min(a.mos, MOS_MAX)})
    St = main_["sticker"]
    mos_now = (1 - a.price / St) if a.price else None          # biên an toàn tại giá hiện tại; âm = giá cao hơn Sticker
    ladder = [dict(mos=l / 100, price=St * (1 - l / 100), reached=bool(a.price and a.price <= St * (1 - l / 100)),
                   need_drop=((St * (1 - l / 100)) / a.price - 1) if a.price else None) for l in levels]
    data = dict(inputs=vars(a), growth_candidates=cands, growth_used=g, growth_how=how, pe_hist_avg=pe_hist, result=main_, sensitivity=sens,
                mos_now=mos_now, mos_ladder=ladder)
    # kiểm tra: khi g = MARR thì Sticker = EPS × P/E
    if abs(g - marr) < 1e-12: assert abs(main_["sticker"] - a.eps * main_["pe"]) < 1e-6
    json.dump(data, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    cur = a.currency
    m = (lambda x: "$" + vn(x, 2)) if cur == "USD" else (lambda x: vn(x, 0) + " đ")
    P = a.price
    def vs(st):
        if not P: return "—"
        return f"{vn(P / st, 2)} lần" if st > 0 else "—"
    rows = "".join(
        f"<tr{' class=\"me\"' if abs(s['g'] - g) < 1e-9 else ''}><td>{vn(s['g'] * 100, 1)}%</td><td><b>{m(s['sticker'])}</b></td><td>{m(s['mos_price'])}</td><td>{vs(s['sticker'])}</td><td>{vn(s['pe'], 1)}</td><td>{m(s['eps_f'])}</td></tr>"
        for s in sens + ([] if any(abs(s['g'] - g) < 1e-9 for s in sens) else [main_]))
    cand_txt = "; ".join(f"{k} {vn(v * 100, 1)}%" if v is not None else f"{k} N/A" for k, v in cands.items()) or "—"
    verdict = ""
    pctm = lambda x: vn(x * 100, 1).replace("-", "−") + "%"
    if P:
        best = max((r["mos"] for r in ladder if r["reached"]), default=None)
        top = ladder[-1]["mos"]
        nxt = next((r["mos"] for r in ladder if not r["reached"]), None)
        if best is not None and nxt is None: verdict = f'<span class="pill p-good">MOS hiện tại {pctm(mos_now)} — đạt bậc cao nhất {vn(top * 100, 0)}%</span>'
        elif best is not None: verdict = f'<span class="pill p-warn">MOS hiện tại {pctm(mos_now)} — qua bậc {vn(best * 100, 0)}%, chưa tới {vn(nxt * 100, 0)}%</span>'
        elif P <= main_["sticker"]: verdict = f'<span class="pill p-warn">MOS hiện tại {pctm(mos_now)} — chưa tới bậc {vn(ladder[0]["mos"] * 100, 0)}%</span>'
        else: verdict = f'<span class="pill p-bad">Giá cao hơn Sticker {vn((P / main_["sticker"] - 1) * 100, 0)}% — MOS âm</span>'
    e = html.escape
    def lrow(r):
        if not P: return f"<tr><td><b>{vn(r['mos'] * 100, 0)}%</b></td><td><b>{m(r['price'])}</b></td><td>—</td><td>—</td></tr>"
        st = '<span class="pill p-good">Đạt</span>' if r["reached"] else '<span class="pill p-bad">Chưa đạt</span>'
        gap = "đã thấp hơn" if r["reached"] else f"giá cần giảm thêm {pctm(-r['need_drop'])}"
        return f"<tr><td><b>{vn(r['mos'] * 100, 0)}%</b>{' (tối đa, mức chuẩn Phil Town)' if abs(r['mos'] - MOS_MAX / 100) < 1e-9 else ''}</td><td><b>{m(r['price'])}</b></td><td>{gap}</td><td>{st}</td></tr>"
    ladder_html = ""
    if ladder:
        now_row = (f'<tr class="me"><td><b>{pctm(mos_now)}</b> — giá hiện tại</td><td><b>{m(P)}</b></td><td>= {vn(P / St * 100, 1)}% của Sticker</td><td>{"MOS âm: giá cao hơn Sticker" if mos_now < 0 else "biên an toàn đang có"}</td></tr>' if P else "")
        ladder_html = f"""<h3>Biên an toàn (MOS) so với Sticker Price</h3>
  <div class="tw"><table>
    <tr><th>Biên an toàn</th><th>Giá mua tương ứng</th><th>So với giá hiện tại</th><th>Trạng thái</th></tr>
    {now_row}
    {''.join(lrow(r) for r in ladder)}
  </table></div>
  <p class="note">Biên an toàn tại một mức giá = 1 − giá ÷ Sticker. {f"Tại {m(P)}: 1 − {m(P)} ÷ {m(St)} = <b>{pctm(mos_now)}</b>. " if P else ""}Giá mua ở bậc MOS x% = Sticker × (1 − x%). Bậc 50% là mức mua chuẩn của Phil Town và là bậc tối đa trong báo cáo; 20%, 30%, 40% là các bậc trung gian để biết giá đang ở đâu trên đường về vùng mua.</p>"""
    sec = f"""<section class="card" id="sticker">
  <h2>Sticker Price (Phil Town) {verdict}</h2>
  <div class="pricebox">
    <div><span class="l">Sticker Price</span><span class="v">{m(main_['sticker'])}</span></div>
    <div><span class="l">Giá mua MOS {vn(a.mos, 0)}%</span><span class="v">{m(main_['mos_price'])}</span></div>
    {f'<div><span class="l">Giá tham chiếu{(" " + e(a.price_date)) if a.price_date else ""}</span><span class="v">{m(P)}</span></div>' if P else ''}
    {f'<div><span class="l">Biên an toàn tại giá hiện tại</span><span class="v">{pctm(mos_now)}</span></div>' if P else ''}
  </div>
  {ladder_html}
  <div class="tw"><table>
    <tr><th>Bước</th><th>Đầu vào</th><th>Giá trị</th></tr>
    <tr><td>1</td><td>EPS 12 tháng gần nhất</td><td><b>{m(a.eps)}</b></td></tr>
    <tr><td>2</td><td>Tăng EPS 10 năm (g)</td><td><b>{vn(g * 100, 1)}%/năm</b></td></tr>
    <tr><td>3</td><td>P/E sau 10 năm</td><td><b>{vn(main_['pe'], 1)}</b></td></tr>
    <tr><td>4</td><td>MARR</td><td><b>{vn(a.marr, 0)}%</b></td></tr>
  </table></div>
  <ul class="note">
    <li><b>EPS:</b> {e(a.eps_note) or '—'}</li>
    <li><b>g:</b> ứng viên {e(cand_txt)}; chọn {e(how)}.{(' ' + e(a.growth_note)) if a.growth_note else ''}</li>
    <li><b>P/E:</b> nhỏ hơn giữa 2 × g = {vn(2 * g * 100, 1)} và P/E trung bình lịch sử {vn(pe_hist, 1) if pe_hist else 'N/A'}{f' ({e(a.pe_hist)})' if a.pe_hist else ''}.</li>
    <li><b>MARR:</b> lợi nhuận tối thiểu chấp nhận được theo Phil Town.</li>
  </ul>
  <p class="note">EPS sau 10 năm = {m(a.eps)} × (1 + {vn(g * 100, 1)}%)¹⁰ = <b>{m(main_['eps_f'])}</b> · Giá sau 10 năm = × P/E {vn(main_['pe'], 1)} = <b>{m(main_['price_f'])}</b> · Sticker = ÷ (1 + {vn(a.marr, 0)}%)¹⁰ ({vn((1 + marr) ** 10, 2)}) = <b>{m(main_['sticker'])}</b> · Giá MOS = × {vn(1 - mos, 2)} = <b>{m(main_['mos_price'])}</b>.</p>
  <div class="tw" style="margin-top:12px"><table>
    <tr><th>Tăng EPS/năm</th><th>Sticker</th><th>Giá MOS {vn(a.mos, 0)}%</th><th>Giá ÷ Sticker</th><th>P/E sau 10 năm</th><th>EPS sau 10 năm</th></tr>
    {rows}
  </table></div>
  <p class="note">Sticker Price rất nhạy với g và P/E tương lai; dùng cùng DCF/Owner Earnings, không thay thế. Không lấy trung bình các phương pháp.</p>
  <div class="gloss"><div><b>Sticker Price</b>: giá hợp lý hôm nay để đạt đúng MARR mỗi năm nếu giả định đúng. <b>MARR</b>: lợi nhuận tối thiểu chấp nhận được. <b>MOS</b> (Margin of Safety, biên an toàn): giá đang thấp hơn Sticker bao nhiêu %; số âm là giá cao hơn Sticker. <b>Giá MOS</b>: Phil Town mua khi giá bằng một nửa Sticker (MOS 50%); các bậc 20%, 30%, 40% là mốc trung gian, 50% là tối đa. <b>BVPS</b>: giá trị sổ sách mỗi cổ phiếu; tăng BVPS là thước đo tăng trưởng Phil Town ưu tiên.</div></div>
</section>
"""
    open(a.out.rsplit(".", 1)[0] + ".html", "w", encoding="utf-8").write(sec)
    print(json.dumps(dict(g=g, how=how, pe=main_["pe"], sticker=main_["sticker"], mos=main_["mos_price"], mos_now=mos_now,
                          ladder={f"{vn(r['mos'] * 100, 0)}%": round(r["price"], 2) for r in ladder}), ensure_ascii=False))


if __name__ == "__main__":
    main()
