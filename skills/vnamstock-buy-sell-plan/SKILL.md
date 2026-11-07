---
name: vnamstock-buy-sell-plan
description: Kế hoạch mua bán cổ phiếu của người dùng trong VNamStock (mua, giữ 5–10 năm, bán; tên cũ: kế hoạch giữ). Từ giá vốn, số cổ phiếu đã mua, cổ tức tiền mặt và cổ tức cổ phiếu mỗi năm, giá định bán sau 5–10 năm, lập báo cáo HTML 4 bảng (lợi nhuận khi giá giữ nguyên, bán sau 5 năm, bảng đầu tư thêm nếu người dùng có kế hoạch, bán sau 10 năm, giá bán ↔ số năm giữ tương đương). Dùng khi người dùng hỏi kế hoạch mua bán, báo cáo mua bán, giữ dài hạn, tỷ lệ Kelly, lãi kép từ cổ tức, "giữ 5–10 năm bán giá X thì lãi bao nhiêu".
---

# Kế hoạch mua bán (VNamStock)
Version: 1.3.0

Trả lời tiếng Việt. Người dùng thường định giữ **5–10 năm**. Skill này chỉ tính kế hoạch theo giả định của người dùng; không thay thế định giá (vnamstock-full-report) và không phải tư vấn đầu tư cá nhân. Áp dụng quy tắc "Giải thích thuật ngữ cho người dùng" của `../vnamstock/SKILL.md`.

## 1. Thu thập đầu vào
Hỏi người dùng (AskUserQuestion hoặc trong chat) những gì chưa có trong tin nhắn:
1. **Mã cổ phiếu**, **giá vốn bình quân** (đ/cp) và **số cổ phiếu đã mua**. Không tự giả định vị thế.
2. **Giá định bán**: chỉ hỏi một giá định bán sau 5 năm (mốc). Nếu người dùng muốn giá khác cho mốc 10 năm thì hỏi thêm; mặc định dùng cùng giá.
3. **Kế hoạch đầu tư thêm**: hỏi người dùng có định bỏ thêm tiền không, bao nhiêu (vd 100 triệu). Có thì truyền `--add-amount` để lập bảng 2b; không thì bỏ bảng này.

Tự tìm, rồi xác nhận lại với người dùng nếu không chắc:
4. **Cổ tức tiền mặt đ/cp/năm** và **cổ tức cổ phiếu %/năm**. Lấy lịch sử chi trả 3–5 năm gần nhất và kế hoạch ĐHCĐ năm nay (công bố trên website doanh nghiệp, HOSE/HNX, CafeF/Vietstock). % cổ tức ở Việt Nam tính trên mệnh giá 10.000 đ (20% = 2.000 đ/cp). Nếu các năm khác nhau, dùng mức kế hoạch/gần nhất và ghi căn cứ. Không tìm được thì hỏi người dùng, không tự bịa.
5. Tùy chọn cho phần "khả thi": giá thị trường hiện tại (ngày, nguồn), số cổ phiếu lưu hành (triệu cp), LN mẹ 4 quý gần nhất (tỷ đ). Có sẵn trong `<ROOT>/<MA>/` (BasicMetrics, valuation) thì dùng lại; thiếu thì lấy bằng `../vnamstock/scripts/cafef_export.py` hoặc bỏ phần khả thi.

6. **Kế hoạch mua bán + Kelly** (khi người dùng nêu vùng mua, giá bán và xác suất lên/xuống, hoặc hỏi "tỷ lệ Kelly"): lấy vùng mua (vd 28.000–30.000 đ), giá nếu đúng (thường = giá định bán), xác suất p và giá nếu sai. Người dùng chưa mua thì dùng `--planned`, `--buy-price` = giữa vùng mua, `--shares` = số cp minh họa (vd ~100 triệu ÷ giá, lô 100) và ghi rõ là minh họa — không tự coi là vị thế thật. Thiếu p hoặc giá nếu sai thì hỏi, không tự đặt.

## 2. Tính và lập báo cáo
Chạy script (không tính tay):
```bash
python -I ~/.claude/skills/vnamstock-buy-sell-plan/scripts/buy_sell_plan.py --symbol FPT --name "FPT Corp" \
  --buy-price 50000 --shares 2000 --dps 2000 --stock-pct 10 --sell-price 100000 \
  --market-price 52700 --market-date 30/10/2026 --shares-out 1885.727648 --ttm-profit 10280.9 \
  --add-amount 100000000 --div-note "..." --sources "Tên::https://..." \
  --out <ROOT>/FPT/FPT-VNamStock-KeHoachMuaBan-YYYY-MM-DD.html
```
Tham số khác: `--sell-price-long` (giá bán mốc 10 năm), `--anchor-years 5`, `--long-years 10`, `--buy-ladder 70000,60000,...` (mặc định: bậc giá tròn ~10% giá thị trường, từ khoảng 1,2 × max(giá vốn, giá thị trường) **xuống dưới nửa giá thị trường hiện tại**, cộng giá vốn và giá thị trường — người dùng dùng để lên kế hoạch mua thêm; luôn truyền `--market-price`), `--pe-assume 15`. Script ghi kèm file `.json` cùng tên.

Tham số Kelly (bật mục Kelly khi có `--kelly-p` và `--kelly-down`): `--kelly-p 0.5 --kelly-up 55000 --kelly-down 20000 --buy-zone 28000-30000 [--planned] [--value-notes "<đối chiếu định giá VNamStock cùng ngày>"]`.

Mô hình Kelly (2 kết cục cho cả kỳ N năm, chỉ tính giá):
- Mua ở P: lãi nếu đúng b = giá_lên/P − 1, lỗ nếu sai l = 1 − giá_xuống/P. f* = p/l − (1 − p)/b (Kelly cho tài sản, Thorp). Kỳ vọng = p·b − (1 − p)·l. p hòa vốn = l/(l + b).
- f* ≤ 0 → "không mua". f* > 100% → công thức muốn vay; mặc định không dùng margin nên trần 100%. Luôn hiện ½ Kelly (khuyên dùng) và ¼ Kelly vì p là ước đoán chủ quan.
- Lãi kép/năm kỳ vọng = e^(tăng trưởng log kỳ vọng ÷ N) − 1 trên tổng vốn khi đặt ½ Kelly (phần còn lại coi như tiền mặt 0%).
- Luôn có 2 bảng độ nhạy ở giá giữa vùng mua: (a) xác suất p ± 5–20 điểm × giá nếu sai; (b) giá nếu đúng ±10–20%.
- Bắt buộc đối chiếu giá nếu đúng/xác suất với định giá VNamStock cùng ngày (DCF/OE/MOS, 4M, CAN SLIM) trong `--value-notes`; nếu giá mục tiêu cao hơn kịch bản lạc quan, nói rõ p 50% là lạc quan.
- Mô hình giả định giữ tới khi chạm 1 trong 2 mức, không có cắt lỗ 7–8% — chỉ dùng cho chiến lược tích trữ/giữ dài hạn; không dùng để định cỡ vị thế CAN SLIM. Không thay quyết định của người dùng về tỷ trọng; chỉ đưa số tiền khi người dùng cho tổng vốn.

Kịch bản cổ tức (bắt buộc từ 1.2.0 khi doanh nghiệp trả cổ tức không đều hoặc có chia cổ phiếu):
- `--div-history "thời điểm|tiền|cổ phiếu|ghi chú; ..."`: lịch sử chi trả 5–7 năm (CafeF LichSuKien + công bố), gồm cả phát hành riêng lẻ/quyền mua vì chúng cũng tăng số cp. Đối chiếu với thay đổi vốn điều lệ trên CĐKT.
- `--div-scenarios "tên:đ/cp:%cp[:%tăng tiền]; ..."`: tối thiểu (1) như năm gần nhất, (2) chỉ tiền mặt, (3) cổ phiếu cách năm/thấp hơn, (4) cổ tức tiền tăng dần nếu có cơ sở, (5) bình quân lịch sử. Bảng hiện tổng tiền bán sau 5/10 năm, lãi kép/năm, "tương đương giá hôm nay" và LN cần tăng/năm ở P/E giả định cho từng kịch bản — để người dùng thấy chia nhiều cổ phiếu thì giá bán càng khó đạt.
- `--dps-growth 10`: cổ tức tiền mặt đ/cp tăng %/năm cho bảng chính (năm 1 = `--dps`). Mặc định 0. Bảng "giá bán ↔ năm giữ" vẫn dùng tốc độ tăng cp năm đầu (xấp xỉ khi có dps-growth).
- Dòng trùng tham số bảng chính được gắn nhãn "bảng chính". Nói rõ bảng chính lạc quan hay thận trọng so với lịch sử.

Mô hình cố định — **Luôn tái đầu tư cổ tức**, không làm cột A/B hay kịch bản không tái đầu tư:
- Mỗi năm, trên số cp đầu năm: nhận cổ phiếu thưởng (× % cp) và tiền mặt (× cổ tức) rồi mua thêm cp ở giá mua → số cp × (1 + % cp + cổ tức/giá mua). Số cp của người dùng dùng chung cho mọi giá mua so sánh.
- Tổng tiền khi bán = số cp cuối kỳ × giá bán. Ghi rõ giả định mua lại ở giá mua ban đầu (lạc quan nếu giá tăng dần).
- Giá bán ↔ năm giữ: số năm (lẻ, quy ra năm/tháng) để tổng tiền ở giá bán ×0,7…×1,4 bằng tổng tiền khi bán giá mốc sau 5 năm, tính theo giá vốn của người dùng.

## 3. Báo cáo HTML (thứ tự cố định)
Lưu `<ROOT>/<MA>/<MA>-VNamStock-KeHoachMuaBan-YYYY-MM-DD.html`, không ghi đè (thêm `_vNN`). CSS ở `assets/style.css` (cùng bộ với báo cáo tổng hợp, có sáng/tối, cuộn ngang trên điện thoại). Mẫu đã duyệt: `assets/report-template-KeHoachMuaBan-FPT.html`.
1. Tiêu đề + **tóm tắt kế hoạch của người dùng** (vốn, tổng tiền bán sau 5 và 10 năm, sau thuế) + điều kiện để kế hoạch đúng.
1b. **Tỷ lệ Kelly** (khi có tham số Kelly, viền nổi bật, đặt ngay sau tóm tắt, trước thanh menu): 4 ô (Kelly ở giữa vùng mua, kỳ vọng, ½ và ¼ Kelly, p hòa vốn), bảng theo giá mua (lãi nếu đúng | lỗ nếu sai | kỳ vọng | Kelly đầy đủ | ½ | ¼ | lãi kép/năm kỳ vọng | p hòa vốn), khung cách đọc, đối chiếu định giá, 2 bảng độ nhạy, chú thích.
1c. **Kịch bản cổ tức** (khi có `--div-scenarios`, ngay sau mục Kelly): bảng lịch sử cổ tức đã trả, bảng kịch bản, khung "đọc đúng" (cổ phiếu thưởng không tạo ra tiền).
2. **Giữ 5 năm, giá không đổi**: giá mua | so với giá TT | vốn | số cp sau 5 năm | **tổng số tiền** | tổng tăng | lãi kép/năm. Các dòng giá mua luôn kéo xuống dưới nửa giá thị trường hiện tại.
3. **2 · Bán sau 5 năm** ở giá định bán: giá mua | vốn | số cp khi bán | tổng tiền khi bán | tổng lãi | lãi kép/năm.
4. **3 · Mua thêm X tr, bán sau 5 năm** (chỉ khi có `--add-amount`) – đúng cột bảng trên, chỉ thêm 1 cột **Cp mua thêm** (lô 100 cp); vốn = tiền dùng, chỉ tính phần tiền mới. Không thêm cột khác.
5. **4 · Bán sau 10 năm** – như bảng bán 5 năm.
6. **5 · Mua thêm X tr, bán sau 10 năm** (khi có `--add-amount`) – như bảng mua thêm 5 năm.
7. **6 · Giá bán ↔ năm giữ, mốc 5 năm** – giá bán | số năm giữ tương đương | so với mốc | lãi kép/năm (trên vốn của người dùng).
7b. **7 · Giá bán ↔ năm giữ, mốc 10 năm** – như trên, mốc bán giá định bán sau 10 năm.
Số mục tự đánh lại (có mua thêm: 1–7, không: 1–5). Tiêu đề ngắn gọn, vd "2 · Bán sau 5 năm, giá 100.000 đ", "3 · Mua thêm 100,0 tr, bán sau 5 năm giá 100.000 đ".
8. Khả thi (nếu có dữ liệu): tương đương giá hôm nay, vốn hóa, lợi nhuận cần tăng/năm ở P/E giả định và P/E hiện tại.
9. Thuế ước tính cho dòng giá vốn của người dùng (5% cổ tức tiền, 0,1% giá bán, 5% × mệnh giá cp thưởng).
10. Giải thích thuật ngữ, nguồn.
Dòng giá vốn của người dùng được tô nổi; dòng giá thị trường có viền vàng. Mỗi bảng có khung `.gloss` chú thích ngay dưới.

Mở thử ở 375px: không tràn ngang trang, bảng cuộn trong khung, đọc được ở sáng/tối.

## 4. Trả lời trong chat
- Đưa 4 bảng rút gọn theo cùng thứ tự (có thể chỉ giữ dòng giá vốn của người dùng và 2–3 dòng so sánh), chú thích thuật ngữ dưới mỗi bảng.
- Luôn nhắc: cổ tức cổ phiếu tự nó không tạo ra tiền; kế hoạch chỉ đúng nếu lợi nhuận tăng ≥ % cổ phiếu chia mỗi năm. Nối với hai quy tắc bán của chuyên gia (tăng trưởng đình trệ 2–3 quý, người nội bộ bán nhiều): giữ 5–10 năm không có nghĩa bỏ qua tín hiệu bán.
- Gửi đường dẫn file HTML. Không đặt lệnh, không gửi email, không lập lịch.
