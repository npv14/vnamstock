---
name: vnamstock-full-report
description: Báo cáo tổng hợp VNamStock cho một mã cổ phiếu, gộp định giá và phân tích cơ bản theo thứ tự đã duyệt — (1) tổng quan định giá NCAV/DCF/Owner Earnings × 3 kịch bản + giá mua MOS, (2) phân tích cơ bản 5 năm + 5 kịch bản giá CafeF, (3) chi tiết định giá. Dùng khi người dùng yêu cầu định giá, phân tích doanh nghiệp, báo cáo cơ bản/phân tích cơ bản/chỉ số cơ bản hoặc báo cáo đầy đủ một mã (không còn báo cáo cơ bản riêng).
---

# Báo cáo tổng hợp VNamStock: định giá + phân tích cơ bản
Version: 1.1.0 (07/11/2026: gộp hẳn skill cơ bản vào đây — “báo cáo cơ bản” = báo cáo Tổng hợp)
Trước đó: 1.0.0 (02/11/2026, theo yêu cầu người dùng: “gộp skill định giá và phân tích cơ bản thành 1 skill, tổng quát về định giá trước, rồi phân tích cơ bản, xong rồi chi tiết về định giá sau”)

Trả lời tiếng Việt. Skill này là lớp ghép báo cáo: nó không thay thế và không viết lại quy tắc của các skill nguồn. Đọc và áp dụng nguyên vẹn:
- `../vnamstock/SKILL.md` — quy trình chung, hai quy tắc bán của chuyên gia, giải thích thuật ngữ, kiểm định.
- Định giá: stock-valuation-from-image nếu truy cập được; nếu không, `../vnamstock/references/stock-valuation.md` + `../vnamstock/references/valuation-rules.md` (bản dự phòng 1.2.1) và `../vnamstock/references/cafef-and-conditional-dcf.md`.
- Cơ bản (Phần 2): `references/basic-metrics.md` và script `scripts/five_year_metrics.py` (chuyển từ skill cafef-basic-scenarios đã gỡ).
- Kiểm định: `../validation-check/SKILL.md` một lần cho cả báo cáo.

Không còn báo cáo cơ bản (CoBan) riêng: khi người dùng nói “báo cáo cơ bản”, “phân tích cơ bản”, “chỉ số cơ bản” hay “giá tăng/giảm 20%, 40%” của một mã, luôn làm báo cáo Tổng hợp này. Người dùng yêu cầu rõ “chỉ định giá” → mẫu KDH cũ. CAN SLIM và 4M có mẫu riêng, không gộp vào đây.

## Khi nào dùng
Người dùng yêu cầu định giá, phân tích doanh nghiệp, “báo cáo đầy đủ/tổng hợp”, “báo cáo cơ bản”, “phân tích cơ bản” hoặc chỉ số cơ bản/kịch bản giá của một mã. Lọc VN30/rổ mã thì chỉ làm bảng xếp hạng ngắn, không chạy skill này cho từng mã.

## Thu thập và tính (làm một lần, dùng chung cho cả 3 phần)
1. Xác định mã/sàn/ngành, ngày phân tích, giá tham chiếu (ghi rõ đóng cửa hay trong phiên, ngày, nguồn), số cổ phiếu hiện hành sau thưởng/ESOP. Dùng **cùng một giá và cùng một số cổ phiếu** cho mọi bảng.
2. Lấy dữ liệu CafeF: `../vnamstock/scripts/cafef_export.py <MA> --root <ROOT> --date YYYY-MM-DD` (4 bảng BCTC) và `python -I scripts/five_year_metrics.py --symbol <MA> --out <ROOT>/<MA>/BasicMetrics/YYYY-MM-DD_vNN [--price P] [--shares SL] [--ttm-ln-me ... --ttm-label ...] --section-class card`. Tìm thêm BCTC/công bố chính thức, giao dịch người nội bộ theo vnamstock.
3. Tính định giá bằng code (dựa trên `../vnamstock/scripts/valuation_model_example.py`), lưu script + output trong `<MA>/valuation/`. Tính 12 chỉ số × 5 kịch bản giá theo references/basic-metrics.md, lưu trong `<MA>/BasicMetrics/YYYY-MM-DD_vNN/`.
4. Đối chiếu chéo trước khi viết: LN mẹ bình quân/nền dòng tiền ở DCF khớp bảng 5 năm; cột TTM bảng 5 năm khớp bảng 12 chỉ số; EPS/BVPS/P/E/P/B giống nhau ở mọi phần; số ở Phần 1 đúng bằng số cơ sở/bi quan/lạc quan ở Phần 3. Lệch thì sửa nguồn số, không sửa chữ.

## Thứ tự báo cáo (cố định)
Mẫu: `assets/report-template-TongHop-KDH.html` (ví dụ KDH, ghép từ mẫu KDH định giá + KDH cơ bản). Đọc file mẫu trước khi viết; giữ nguyên CSS, biến màu sáng/tối, `.part` chia phần, thanh menu chia 3 nhóm, cách bảng cuộn ngang trong khung trên điện thoại. Không ép số liệu hay nhận định của KDH sang mã khác.

**Tiêu đề** — mã, tên, sàn, ngày phân tích, giá tham chiếu (ngày, nguồn), kỳ dữ liệu, số cổ phiếu.

**Phần 1 · Tổng quan định giá** (`#phan1`)
1. `#giadinhgia` — bảng giá trị đ/cp: NCAV, DCF 10 năm, Owner Earnings × bi quan/cơ sở/lạc quan, cột “cơ sở so với giá”; 4 ô: giá thị trường + ngày, khoảng giá trị kịch bản cơ sở, cao nhất (lạc quan), giá mua MOS 30% (ghi rõ theo phương pháp nào). Luôn có con số cụ thể (mô hình có điều kiện thì ghi nhãn giả định và độ tin cậy trong 1–2 câu); không mở đầu bằng N/A hay danh sách thiếu dữ liệu.
2. `#tomtat` — 3 ô kết luận ngắn (tăng trưởng · định giá · độ tin cậy) + trạng thái hai quy tắc bán của chuyên gia, mỗi trạng thái có liên kết xuống chi tiết ở Phần 3.
3. Thanh menu `nav` chia 3 nhóm Phần 1/2/3.

**Phần 2 · Phân tích cơ bản** (`#phan2`)
4. `#coban` — thẻ chỉ số chính (giá, BVPS/P/B, NCAV, DCF cơ sở, P/E TTM/cốt lõi, nợ).
5. `#namnam` — bảng 5 năm tài chính gần nhất + TTM + CAGR/TB 5 năm (tăng trưởng, hiệu quả, mỗi cổ phiếu, định giá cuối năm, sức khỏe gồm **tổng nợ phải trả và Nợ/Doanh thu**) + khung “Đọc nhanh 5 năm”. Dán đoạn `five_year_table.html` của script (đã chạy với `--section-class card`, không có viền `price-top` vì viền nổi bật dành cho bảng giá Phần 1).
6. `#bang` — 12 chỉ số × 5 kịch bản giá −40% / −20% / hiện tại / +20% / +40% (k = 0,6/0,8/1/1,2/1,4); thêm P/E cốt lõi khi có lãi bất thường lớn.
7. `#the` — thẻ tóm tắt từng kịch bản (đọc dễ trên điện thoại).
8. `#doichieu` — đối chiếu số CafeF với số tự tính.
9. `#nhanxet` — nhận xét phân tích cơ bản, câu cuối nối sang giá trị ước tính ở Phần 1/Phần 3 (không ghi “báo cáo này không định giá DCF”).

**Phần 3 · Chi tiết định giá** (`#phan3`)
10. `#pe` — P/E · PEG (TTM báo cáo, TTM cốt lõi, chuẩn hóa, forward nếu có; PEG không có ý nghĩa khi tăng trưởng ≤0).
11. `#taisan` — NWC và NCAV (sổ sách + 2 mức haircut, 2/3 NCAV). Ngân hàng/bảo hiểm: thay bằng phương pháp phù hợp và ghi lý do.
12. `#dcf` — DCF 10 năm 3 kịch bản (CF0, g, r/gT, PV 10 năm, PV TV và tỷ trọng), định giá ngược, bảng độ nhạy r × gT, giá mua MOS 15/25/30/50%.
13. `#oe` — Owner Earnings 3 kịch bản, nêu rõ capex/tái đầu tư duy trì là giả định nếu chưa có thuyết minh.
14. `#payback` — payback FCF/FCFE và OE: không tăng trưởng, tăng trưởng không chiết khấu, chiết khấu; không cộng TV.
15. `#quy` — Quy tắc bán ① tăng trưởng đình trệ 2–3 quý: biểu đồ cột LN cốt lõi so với cùng kỳ, bảng quý, khung trạng thái.
16. `#noibo` — Quy tắc bán ② người nội bộ: bảng giao dịch + kết luận.
17. `#ruiro` — rủi ro và việc cần kiểm tra ở báo cáo sau.
18. `#kiemdinh` — một bảng chung, chia nhóm “Phần 2 — Phân tích cơ bản” và “Phần 1 & 3 — Định giá”, có dòng “Phần 1 khớp Phần 3”.
19. `#thuatngu` — giải thích thuật ngữ đầy đủ (gộp, không lặp mục).
20. `#nguon` (footer) — nguồn của cả hai phần, bỏ trùng URL; đường dẫn thư mục dữ liệu và script.

Mỗi phần có khung `.gloss` chú thích nhỏ ngay bên dưới, chỉ cho thuật ngữ xuất hiện trong phần đó, theo `../vnamstock/references/glossary.md` (quy tắc “Giải thích thuật ngữ cho người dùng” trong vnamstock).

## Lưu và trả kết quả
- Lưu tại `<ROOT>/<MA>/<MA>-VNamStock-TongHop-YYYY-MM-DD.html`, không ghi đè (thêm `_vNN` nếu trùng ngày). Dữ liệu ở `<MA>/CafeF/`, `<MA>/BasicMetrics/`, `<MA>/valuation/`.
- Mở thử: không tràn ngang ở 375px, đọc được ở chế độ sáng và tối, mọi liên kết `#...` trong menu trỏ đúng id.
- Trả lời chat theo cùng thứ tự: bảng giá định giá trước (kèm chú thích thuật ngữ), vài dòng cơ bản, rồi tóm tắt chi tiết/rủi ro; gửi đường dẫn file HTML.
- Đây là phân tích theo khung quy tắc của chuyên gia, không phải tư vấn đầu tư cá nhân hóa; không đặt lệnh, không tự gửi email hay lập lịch.
