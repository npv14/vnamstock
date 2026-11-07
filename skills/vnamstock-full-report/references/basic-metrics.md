# Phần 2 báo cáo Tổng hợp: chỉ số cơ bản và kịch bản giá CafeF
(Chuyển từ skill cafef-basic-scenarios đã gỡ ngày 07/11/2026; không còn báo cáo CoBan riêng.)

Trả lời tiếng Việt, tính kết quả cụ thể dù dữ liệu chưa hoàn hảo, ghi rõ giả định và phần chưa chắc chắn. Nếu thiếu mã cổ phiếu, suy ra từ yêu cầu hiện tại/ảnh khi rõ ràng; nếu không thì hỏi mã.

## Lấy và lưu dữ liệu

- Mỗi lần chạy lấy dữ liệu mới từ trang cổ phiếu CafeF đúng sàn và mã. Ghi ngày giờ lấy, ngày giao dịch của giá, kỳ BCTC của chỉ số. Không gọi giá cũ là giá hôm nay hoặc giá trong phiên là giá đóng cửa.
- Ưu tiên công cụ đọc web/API công khai; khi cần dùng trình duyệt để đọc bảng hoặc tìm request thực tế của trang. Endpoint giá đã dùng được: `https://cafef.vn/du-lieu/Ajax/PageNew/RealtimePricesHeader.ashx?symbols=MBB` (thay mã). Đây là API nội bộ có thể đổi, không phải API được cam kết. Kiểm tra schema, đơn vị, thời gian; không mặc định mọi trường giá đều là đồng. Giá `19.7` ở endpoint này thường biểu diễn 19.700 đồng, cần đối chiếu bảng giá.
- Thu thập đủ bộ trong ảnh mẫu: giá, vốn hóa, cổ phiếu lưu hành, tỷ suất cổ tức, ROA, ROE, free float, P/E, EPS, BVPS (giá trị sổ sách/cp), beta, P/B, khối lượng giao dịch trung bình 10 phiên. Chỉ số không có thì ghi N/A và lý do, không tự điền 0.
- Ảnh người dùng là nguồn bổ sung có mốc riêng; không gắn nhãn số từ ảnh là số mới lấy CafeF. Nếu CafeF không truy cập được, dùng ảnh/dữ liệu đã lưu để tính phần khả dụng, nêu rõ chưa cập nhật trực tuyến. Với lỗi tạm thời thử lại tối đa 2 lần rồi dùng phương án khác.
- Lưu dữ liệu vào `<ROOT>/<MA>/BasicMetrics/YYYY-MM-DD_vNN/` hoặc thư mục project người dùng chỉ định: dữ liệu gốc đọc được, `inputs.json`, bảng kết quả CSV, script tính. Kết quả đưa vào Phần 2 của báo cáo Tổng hợp `<MA>-VNamStock-TongHop-YYYY-MM-DD.html`; footer ghi đường dẫn thư mục dữ liệu. Không ghi đè lần trước. Mỗi đầu vào cần giá trị, đơn vị, URL/nguồn ảnh, kỳ và thời điểm lấy; phân biệt nguồn báo cáo và số tính lại.

## Bảng so sánh 5 năm (bắt buộc, đặt đầu tiên)

Phần 2 phải mở đầu (trước bảng 12 chỉ số × 5 kịch bản) bằng bảng so sánh chỉ số 5 năm tài chính gần nhất + cột TTM/hiện tại + cột CAGR/trung bình 5 năm. Chạy:

`python -I ../scripts/five_year_metrics.py --symbol <MA> --out <ROOT>/<MA>/BasicMetrics/YYYY-MM-DD_vNN [--price P] [--shares SL_cp_hien_hanh] [--ttm-ln-me LN_4_quy --ttm-label "Q4/25–Q3/26"]`

- Script lấy BCTC năm (GetReportSummary + GetReportLCTT, TypeTime=NAM, 2 trang), BCTC quý, giá đóng cửa cuối mỗi năm (PriceHistory có StartDate/EndDate); lưu `raw/`, `five_year.json`, `five_year.csv` và `five_year_table.html` (đoạn `<section id="namnam">` dán thẳng vào báo cáo; hàm `render()` dùng lại được khi cần chỉnh số).
- Nhóm chỉ tiêu: Tăng trưởng (doanh thu, LN mẹ, % so năm trước) · Hiệu quả (biên gộp, biên ròng, ROE, ROA) · Mỗi cổ phiếu (EPS, BVPS quy về cổ phiếu hiện hành) · Định giá cuối năm (giá chưa điều chỉnh, P/E, P/B = vốn hóa cuối năm ÷ LN mẹ/VCSH mẹ, tỷ suất cổ tức tiền đã trả) · Sức khỏe (**tổng nợ phải trả, Nợ phải trả/Doanh thu** — bắt buộc theo yêu cầu người dùng 29/10/2026, Nợ/VCSH, CFO, CFO/LN mẹ, FCF).
- Khi CafeF chưa có quý mới nhất mà đã có KQKD công bố, truyền `--ttm-ln-me`; ghi chú rõ doanh thu/biên TTM vẫn theo 4 quý CafeF. Cột TTM phải khớp bảng 12 chỉ số bên dưới (ROE, ROA, BVPS, P/B); nếu cách tính khác thì sửa số TTM theo bảng 12 chỉ số trước khi `render()` và ghi lại trong json.
- Số 0 bất thường từ CafeF (ví dụ đầu tư TSCĐ = 0) là thiếu dữ liệu → N/A, không tính FCF. Ngân hàng/bảo hiểm: schema khác, dòng thiếu ra N/A; thay bằng NIM, nợ xấu, CIR khi có nguồn.
- Thêm khung “Đọc nhanh 5 năm” 3–4 gạch đầu dòng trong section: xu hướng tăng trưởng (CAGR, năm chậm lại), độ ổn định ROE/biên, P/E · P/B hiện tại so với trung bình 5 năm, **nợ so với doanh thu** (CAGR nợ vs CAGR doanh thu, năm nào Nợ/Doanh thu tăng và nợ tăng ở khoản nào nếu biết), và các điểm làm số không cùng nền (tách/sáp nhập công ty con, thưởng cổ phiếu, thiếu dữ liệu).
- Ví dụ cũ (chỉ tham khảo cách trình bày): `<ROOT>/FPT/FPT-VNamStock-CoBan-2026-10-29_v02.html`.
- Luôn chạy với `--section-class card`: bảng 5 năm nằm ở Phần 2, sau bảng giá định giá; viền nổi bật `price-top` để dành cho bảng giá Phần 1. 

## Đối chiếu trước khi tính

- Chuẩn hóa giá/EPS/BVPS/cổ tức về đồng/cp; cổ phiếu về số lượng; vốn hóa về đồng rồi trình bày tỷ đồng; tỷ lệ phần trăm có đơn vị rõ ràng.
- Kiểm tra `vốn hóa ≈ giá × số cổ phiếu`, `P/E ≈ giá/EPS`, `P/B ≈ giá/BVPS`. Nếu sai lệch vượt làm tròn, hiển thị cả chỉ số nguồn và số tự tính, giải thích khả năng khác ngày, EPS điều chỉnh, kỳ TTM hoặc thay đổi vốn. Không âm thầm sửa dữ liệu để khớp.
- Đối chiếu cổ tức cổ phiếu, chia tách, phát hành quyền mua và EPS/BVPS điều chỉnh. Không trộn giá sau chia với EPS trước chia. Nếu chưa giải quyết được, đưa bảng điều kiện trên một nền đầu vào nhất quán và đánh dấu chưa xác nhận.
- EPS dùng LNST thuộc cổ đông mẹ/cổ phiếu bình quân khi muốn tính EPS kế toán. Nếu dùng cổ phiếu hiện hành để điều chỉnh thì gọi rõ EPS pro forma. BVPS dùng vốn thuộc cổ đông mẹ, trừ NCI đúng một lần. Không lấy giá trị EPS 0 từ API làm dữ liệu thật khi nghi trường bị thiếu.

## Năm kịch bản bắt buộc

Cột theo thứ tự: **−40%, −20%, hiện tại, +20%, +40%**. Đặt hệ số giá k = 0,6; 0,8; 1; 1,2; 1,4. Đây là phép đổi riêng giá cổ phiếu, giữ nguyên hoạt động kinh doanh, số cổ phiếu và chính sách cổ tức. Không phải dự báo kinh doanh.

| Chỉ tiêu | Cách tính ở mỗi kịch bản |
|---|---|
| Giá | P × k |
| Vốn hóa | P × k × số cổ phiếu lưu hành |
| P/E | P × k / EPS; EPS ≤ 0 ghi không có ý nghĩa định giá và giữ EPS thực tế |
| P/B | P × k / BVPS; BVPS ≤ 0 ghi không có ý nghĩa định giá |
| Tỷ suất cổ tức tiền mặt | DPS / (P × k) × 100%; nếu chỉ biết yield hiện tại có thể dùng yield/k và ghi DPS suy ra, không gọi là cổ tức đã xác nhận |
| EPS, BVPS | Giữ nguyên |
| ROA, ROE | Giữ nguyên: thay giá không đổi lợi nhuận hay vốn sổ sách |
| Số cổ phiếu, free float | Giữ nguyên |
| Beta | Giữ số lịch sử tham chiếu; không suy ra beta mới chỉ từ một mức giá giả định |
| KL giao dịch TB 10 phiên | Giữ số lịch sử tham chiếu; không dự báo khối lượng từ giá |

Không nhân tất cả chỉ số với k. Nếu chỉ có P/E hoặc P/B nguồn nhưng thiếu EPS/BVPS, có thể nhân tỷ số nguồn với k, ghi rõ dùng tỷ số nguồn, chưa đối chiếu mẫu số. Không cộng cổ tức cổ phiếu vào dividend yield tiền mặt. Khi DPS chưa rõ kỳ, không suy ra suất sinh lời cổ tức tương lai chắc chắn.

Nếu đưa thêm PEG, cần tăng trưởng EPS cùng nền và cùng kỳ; thiếu thì N/A. Tăng trưởng giả định phải ghi là mô phỏng. Không suy ra giá trị nội tại hoặc thời gian hoàn vốn từ P/E một cách máy móc.

## Báo cáo và kiểm tra

- Thứ tự trong Phần 2: **So sánh chỉ số 5 năm** → bảng đầy đủ 12 chỉ số trong ảnh cộng hàng giá cho cả 5 kịch bản. HTML có thẻ viewport, bảng cuộn ngang trong khung và các thẻ kịch bản dọc hoặc bản tóm tắt dễ đọc trên điện thoại; không phụ thuộc JavaScript để nhìn thấy số liệu.
- Phân biệt màu/ghi chú nhóm thay đổi theo giá và nhóm giữ nguyên. Giải thích ngắn giảm giá làm P/E, P/B, vốn hóa giảm nhưng yield tiền mặt tăng, nếu các đầu vào khác giữ nguyên. Giá giảm không tự chứng minh doanh nghiệp rẻ hay ít rủi ro hơn.
- Kết luận đánh giá bội số theo ngành, nêu vấn đề dữ liệu trọng yếu. Với ngân hàng ưu tiên ROE/PB và chất lượng tài sản; không coi ROA thấp hơn doanh nghiệp công nghiệp là tự động xấu. Định giá DCF nằm ở Phần 1 và 3 của báo cáo Tổng hợp.
- Kiểm tra bằng phép tính: giá/vốn hóa/P/E/P/B tỷ lệ thuận k, yield tỷ lệ nghịch, các trường cố định giống nhau; xử lý mẫu số 0/âm/thiếu. Giữ độ chính xác khi tính, chỉ làm tròn khi trình bày.
- Trả liên kết báo cáo HTML và dữ liệu lưu, kèm URL CafeF hỗ trợ kết quả. Không tự gửi email hoặc lập lịch theo dõi từ việc chạy skill.

## Giải thích thuật ngữ
Áp dụng mục “Giải thích thuật ngữ cho người dùng” trong ../../vnamstock/SKILL.md: dưới mỗi bảng/phần có chú thích nhỏ cho chữ viết tắt (P/E, P/B, EPS, BVPS, ROA, ROE, beta, free float…), dùng định nghĩa trong ../../vnamstock/references/glossary.md; báo cáo HTML có mục “Giải thích thuật ngữ” ở cuối.
