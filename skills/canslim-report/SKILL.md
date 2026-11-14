---
name: canslim-report
description: Lập báo cáo CAN SLIM cho cổ phiếu Việt Nam hoặc quốc tế trong VNamStock khi người dùng yêu cầu CANSLIM, chấm C A N S L I M, đánh giá cổ phiếu tăng trưởng hoặc điểm mua breakout. Nhận mã cổ phiếu, ảnh, bảng giá hoặc báo cáo tài chính; xuất bảng bằng chứng, kết luận và dữ liệu thiếu.
---

# Báo cáo CAN SLIM của VNamStock
Version: 1.1.0

Đọc ../vnamstock/SKILL.md để áp dụng hai quy tắc bán bổ sung của chuyên gia; không lặp lại việc điều hướng về skill này. Trả lời tiếng Việt mặc định. Đây là báo cáo phân tích trong chat, không tự giao dịch hoặc theo dõi nền. Chỉ tạo PDF/Word khi được yêu cầu, theo skill tài liệu và lưu trữ phù hợp.

## Nguyên tắc CAN SLIM bổ sung của chuyên gia — ưu tiên khi lập báo cáo
Nguồn: ghi chú người dùng tổng hợp từ chuyên gia và ba ảnh slide gửi ngày 27/10/2026. Đây là chiến lược của chuyên gia mà người dùng chọn áp dụng, không phải khẳng định mọi thị trường hay mọi cổ phiếu đều hành xử giống nhau. Các quy tắc này bổ sung và ưu tiên hơn hướng dẫn CAN SLIM mặc định bên dưới nếu có khác biệt.

1. **Market direction là phần quan trọng nhất.** Mở báo cáo bằng M trước khi phân tích mã: thị trường tăng/bull, đi ngang, đang điều chỉnh, giảm/bear hoặc chưa xác định; ghi thời điểm, chỉ số phù hợp, dữ liệu và độ tin cậy. Dựa trên giá–khối lượng, cấu trúc đỉnh/đáy, MA, độ rộng và hành vi cổ phiếu dẫn dắt. Không chỉ nhìn một phiên hoặc chỉ số tăng do vài mã lớn. Nếu thị trường xấu/chưa rõ, ưu tiên bảo toàn vốn/chờ, không để điểm C/A đẹp lấn át M. MA hay proxy không được gọi là xác nhận thị trường chính thức.
2. **Chỉ chọn cổ phiếu dẫn dắt.** Ưu tiên tăng trưởng EPS/lợi nhuận quý và năm, doanh thu, biên lợi nhuận, ROE/ROA tốt so với ngành, cùng sức mạnh giá tích cực. Công ty lớn nhất hoặc thương hiệu nổi tiếng nhất không mặc nhiên dẫn dắt. So sánh cùng kỳ/cùng ngành, xét đòn bẩy và chất lượng lợi nhuận; không dùng ROE cao do vốn nhỏ/nợ cao làm bằng chứng đủ. RS của KFSP nếu có chỉ dùng khi xác minh nguồn, ngày và phương pháp; không gọi là IBD RS Rating hoặc RSI.
3. **Cắt lỗ nhanh.** Ảnh 2 ghi 7–8% từ điểm mua; note văn bản ghi 7–10%. Lưu cả hai, công bố quy ước thực thi mặc định: mốc cắt lỗ 7–8% từ giá mua thực tế, không tự chờ tới 10%. Mức khác trong dải 7–10% phải được người dùng chọn trước cho vị thế, không tự nới khi lỗ. Thiếu giá mua thì hỏi hoặc chỉ đưa công thức, không tạo giá vốn. P_stop=P_entry*(1-s), với s là tỷ lệ đã chọn. Dùng giá khớp thực tế, điều chỉnh sự kiện cổ phiếu nhất quán; phân biệt giá pivot, giá mua, giá vốn và trailing stop. Mỗi lần mua thêm phải có kế hoạch rủi ro; không bình quân lại để che việc chạm stop của phần mua trước. Gap, thanh khoản, biên độ và điều kiện thanh toán có thể khiến lỗ thực tế vượt stop; không hứa khớp đúng mức. Nếu đã vượt stop, cảnh báo vi phạm và ưu tiên đề xuất thoát/giảm rủi ro, không chờ hòa vốn.
4. **Thua ít khi sai quan trọng hơn luôn đúng.** Theo ý ảnh 3: bảo toàn vốn, chấp nhận sai, hạn chế thiệt hại; giá đã tăng không tự nghĩa là đắt và giá giảm sâu không tự nghĩa là rẻ. Không coi giá sẽ tiếp tục đi cùng hướng là điều chắc chắn. Nêu điểm vô hiệu trước điểm kỳ vọng; nếu có quy mô vốn và mức rủi ro do người dùng chọn, có thể tính số cổ phiếu tối đa theo ngân sách rủi ro/(giá vào-stop), có xét phí và thanh khoản. Không tự đặt ngân sách rủi ro thay người dùng.
5. **Lạc quan có căn cứ về tương lai Việt Nam.** Giữ góc nhìn dài hạn tích cực, tìm cơ hội có bằng chứng về doanh nghiệp/năng suất/ngành. Tách triển vọng dài hạn khỏi xu hướng thị trường ngắn hạn. Công bố dữ liệu bất lợi, rủi ro và điều kiện làm thay đổi luận điểm; không sửa số, bỏ cảnh báo hoặc ép kết luận tăng giá để tỏ ra lạc quan.
6. **Tập trung tăng trưởng tốt.** Ưu tiên tăng trưởng bền vững, được doanh thu và dòng tiền xác nhận; tránh chỉ nhìn giá rẻ, P/E thấp, danh tiếng hoặc lợi nhuận một lần. Luôn bổ sung PEG khi đưa P/E theo quy tắc VNamStock, nhưng không để PEG thay thế M/L/điểm mua.
7. **Phân tích kỹ thuật là nền tảng quyết định thời điểm và quản trị rủi ro.** Bắt buộc xem đồ thị ngày/tuần hoặc OHLCV đủ dài, xu hướng, nền giá, pivot, hỗ trợ, giá–khối lượng và điểm vô hiệu; dùng tăng trưởng cơ bản để chọn doanh nghiệp. Thiếu dữ liệu đồ thị thì ghi chưa xác nhận điểm mua, không bịa mẫu hình.

## Những sai lầm phải nhắc khi phù hợp
- Ngoan cố giữ vị thế lỗ hoặc dời stop để hy vọng hòa vốn.
- Bắt đáy chỉ vì giá đang giảm; phân biệt với nhịp điều chỉnh có kiểm soát trong xu hướng tăng đã được xác nhận. Không coi mọi phiên giảm là tín hiệu bán.
- Bình quân giá xuống. Với chiến lược CAN SLIM, chỉ cân nhắc bình quân giá lên khi vị thế/giá đã xác nhận đúng, có điểm bổ sung hợp lệ và tổng rủi ro được kiểm soát; không mua đuổi tùy tiện.
- Không học/đọc đồ thị và không phân loại thị trường chung đang tăng, điều chỉnh hay giảm.
- Bỏ qua sự bảo trợ của tổ chức: kiểm tra I bằng sở hữu và biến động qua kỳ, không suy ra từ khối lượng đơn lẻ.
Câu cuối ghi chú “Tập quan trọng của có đảm bảo của nhà đầu tư” chưa rõ nghĩa. Lưu là điểm cần người dùng làm rõ, không coi cách diễn giải về tổ chức ở trên là ý đã được xác nhận; mục I vốn có vẫn giữ nguyên.

## Thứ tự hành động và định dạng ưu tiên
Đối với CAN SLIM: trình bày M trước → L và chất lượng tăng trưởng → nền giá/điểm vào → stop và quy mô rủi ro → các tiêu chí còn lại. Vẫn xuất đủ bảng C–A–N–S–L–I–M.
Đặt khối đầu báo cáo: “Thị trường chung | Bằng chứng | Độ tin cậy | Hành động phù hợp”. Sau tóm tắt là Bảng 7 tiêu chí, tiếp theo “Minh họa 4 kịch bản”, rồi mới đến “Kế hoạch nếu sai” (thứ tự người dùng yêu cầu ngày 28/10/2026): giá mua/giả định, stop 7% và 8% tham khảo nếu chưa chọn một mức, điểm vô hiệu và tình trạng giá hiện tại. Không gọi mức stop tham khảo là lệnh đã đặt.
Quy tắc cắt lỗ và thị trường có vấn đề áp dụng ngay theo bằng chứng, không đợi quy tắc 2–3 quý tăng trưởng hoặc nội bộ bán. Giữ nguyên hai tín hiệu bán cũ và nêu riêng.
Những nguyên tắc này thuộc chế độ CAN SLIM. Không tự chuyển mọi vị thế dài hạn/Stockpiling sang CAN SLIM hoặc xóa skill định giá. Nếu người dùng kết hợp hai chiến lược, xác định chiến lược cho vị thế và nêu xung đột trước khi đề xuất bình quân giá/mức bán; giá trị DCF không được dùng để bỏ stop của vị thế CAN SLIM.

## Phạm vi và dữ liệu
Xác định mã, sàn, ngày đánh giá và chỉ số thị trường đối chiếu. Nếu chỉ thiếu mã và không suy ra từ ảnh, hỏi mã; nếu có mã, chủ động nghiên cứu. Với phân tích lịch sử, chỉ dùng thông tin đã công bố trước ngày đánh giá, không đưa dữ liệu tương lai vào kết luận.
Đọc ảnh và ghi đơn vị, kỳ, nguồn, phần không rõ. Tìm báo cáo tài chính hợp nhất, thuyết minh, IR, công bố sở giao dịch, lịch sử giá/khối lượng và sở hữu tổ chức có nguồn. Ưu tiên nguồn chính thức; dẫn nguồn cạnh mỗi nhóm số liệu. Ghi ngày công bố, kỳ dữ liệu, ngày truy cập và tình trạng kiểm toán/soát xét.
Lấy tối thiểu 8 quý để tính 4 quý YoY và 4 năm EPS để có 3 mức tăng trưởng năm; lấy 5 năm nếu có. Lấy tối thiểu 252 phiên giá/khối lượng và chuỗi chỉ số cùng ngày để đánh giá L/M. Thiếu một phần vẫn lập báo cáo, ghi “chưa đủ dữ liệu”; không tạo số.
Dùng EPS điều chỉnh chia tách/cổ tức cổ phiếu và pha loãng nhất quán. Lợi nhuận cổ đông mẹ không thay thế EPS một cách im lặng. Quý riêng từ số lũy kế: có thể trừ doanh thu/lợi nhuận, nhưng không trừ EPS lũy kế nếu số cổ phiếu bình quân thay đổi; dùng EPS quý được công bố hoặc tính với mẫu số quý phù hợp. Không annualize một quý theo mùa vụ.

## Tiêu chí báo cáo
Dùng ngưỡng tham chiếu dưới đây, công bố cách đánh giá. Các biến thể CAN SLIM có khác biệt; không tự hạ ngưỡng cho cổ phiếu đang xét. Nếu người dùng chọn ngưỡng khác, ghi rõ “bộ lọc tùy chỉnh”.

| Mục | Nội dung và ngưỡng tham chiếu |
|---|---|
| C — Current quarterly earnings | EPS quý gần nhất dương và tăng YoY ít nhất 25%; xem tăng tốc ở các quý trước. Đối chiếu doanh thu và lợi nhuận cốt lõi để loại hiệu ứng nền thấp/khoản một lần. |
| A — Annual earnings | EPS dương, tăng ít nhất 25% trong từng năm của 3 năm gần nhất theo bộ lọc nghiêm ngặt; trình bày thêm CAGR 3–5 năm. ROE khoảng 17% trở lên là hỗ trợ, không thay thế EPS. |
| N — New | Xác minh sản phẩm, thị trường, quản trị hoặc điều kiện ngành mới; hoặc đỉnh giá mới gắn nền giá hợp lý. Phân biệt kế hoạch với kết quả triển khai. |
| S — Supply and demand | Phân tích cổ phiếu lưu hành/free float, pha loãng, mua lại và giá–khối lượng; đánh giá cầu ở phiên tăng/breakout so với lịch sử. Free float thấp không tự động tốt. |
| L — Leader | So sánh sức mạnh giá và tăng trưởng với chỉ số/ngành, tìm cổ phiếu dẫn đầu. RS Rating chính thức ≥80 là tham chiếu nếu có nguồn. |
| I — Institutional sponsorship | Xác minh tổ chức sở hữu, chất lượng và thay đổi số lượng/tỷ lệ nắm giữ qua các kỳ. Nêu độ trễ báo cáo và mức tập trung. |
| M — Market direction | Đánh giá thị trường chung cùng thời điểm: xu hướng chỉ số, giá–khối lượng, độ rộng và áp lực phân phối nếu có dữ liệu. Tách xu hướng của cổ phiếu với thị trường. |

Công thức YoY=(EPS_t/EPS_cùng_kỳ-1)*100 chỉ diễn giải thông thường khi nền EPS dương; nền 0/âm phải ghi mức chuyển lỗ/lãi, không coi tỷ lệ bất thường là đạt C/A. CAGR=(EPS_cuối/EPS_đầu)^(1/n)-1, n là số khoảng năm, không phải số dòng; kiểm tra chuỗi âm và khoản bất thường. Tách số báo cáo và số chuẩn hóa, nêu phép điều chỉnh.
Mỗi mục ghi: Đạt / Một phần / Không đạt / Chưa đủ dữ liệu, bằng chứng, kỳ, lý do và độ tin cậy. C chỉ “Đạt” khi thỏa EPS và không có mâu thuẫn chất lượng chưa giải quyết. A nếu CAGR cao nhưng một năm không đạt ngưỡng thì không gọi đạt bộ lọc từng năm. Các mục định tính phải giải thích cơ sở, không ép thành số.

## Kiểm tra giá và điểm mua
Không bịa RS Rating/Composite Rating độc quyền, không đồng nhất RSI với relative strength. Nếu không có RS Rating, tính proxy công khai: excess return 3/6/12 tháng so với chỉ số trên cùng chuỗi ngày; chỉ gọi percentile khi có tập cổ phiếu so sánh đủ rộng và mô tả tập mẫu/phương pháp. Proxy không phải IBD RS Rating.
Dùng cùng cơ sở điều chỉnh giá và khối lượng cho sự kiện cổ phiếu; nêu nhà cung cấp và cách điều chỉnh. MA50/MA200, khoảng cách đỉnh 52 tuần và V/khối lượng bình quân 50 phiên TRƯỚC phiên xét là các kiểm tra hỗ trợ của VNamStock, không tự thay thế hệ thống Market Pulse hay xác nhận follow-through day chính thức.
Tách khối lượng khớp lệnh/thỏa thuận khi có thể; không kết luận tổ chức mua chỉ vì khối lượng tăng. Không gọi một phiên tăng là breakout thành công nếu chưa có nền giá và mức pivot kiểm chứng.
Chỉ đưa pivot/vùng mua khi có đủ đồ thị hoặc OHLCV để chỉ ra mẫu hình, thời gian nền và điểm vô hiệu. Nếu ảnh không đọc được giá/trục, chỉ nhận định định tính. Không mặc định giá vượt MA hoặc đỉnh 52 tuần là điểm mua.
Nếu đề cập vùng mua tối đa khoảng 5% trên pivot hoặc cắt lỗ 7–8% dưới giá khớp, kiểm tra nguồn quy tắc CAN SLIM trước khi trình bày, ghi là tham chiếu của phương pháp, không phải lệnh giao dịch. Nêu rủi ro gap, thanh khoản và cơ chế thanh toán thị trường nếu liên quan; không đảm bảo khớp đúng giá.
Không bình quân giá xuống theo logic CAN SLIM hoặc gọi stockpiling là CAN SLIM. Báo cáo CAN SLIM đánh giá tăng trưởng/động lượng, không tự xác lập intrinsic value; chỉ gọi skill Stock Valuation khi người dùng muốn kết hợp định giá.

## Cách tổng hợp
Không tạo “điểm CAN SLIM chính thức” hoặc xác suất thắng. Mặc định đếm số mục theo bốn trạng thái và số mục có dữ liệu trên 7; không đổi mục thiếu dữ liệu thành 0 hoặc đạt. Không lấy tổng điểm để che thị trường xấu hoặc không có điểm mua.
Kết luận theo điều kiện:
- M không thuận lợi: “chờ thị trường”, dù C/A tốt.
- C/A không đáp ứng: “chưa phù hợp bộ lọc tăng trưởng nghiêm ngặt”, không đồng nghĩa doanh nghiệp xấu.
- Dữ liệu quan trọng C/A/L/M thiếu: “chưa đủ cơ sở kết luận”.
- Nền giá/điểm mua chưa xác nhận hoặc đã tăng quá xa: “theo dõi/chờ điểm vào”.
- Chỉ ghi “ứng viên CAN SLIM đáng nghiên cứu” khi bằng chứng hỗ trợ cả cơ bản, dẫn dắt, cung cầu và thị trường; không cam kết lợi nhuận.

P/E và PEG là phần bổ sung theo sở thích người dùng, không phải tiêu chí loại cổ phiếu cốt lõi của CAN SLIM. Nếu đưa P/E thì bắt buộc có PEG hoặc lý do chưa tính được; dùng tăng trưởng EPS có kỳ và nguồn, không dùng doanh thu thay EPS. PEG<1 không tự quyết định mua.

## Quy tắc bán của chuyên gia
Luôn có ô riêng cho: (1) không tăng trưởng cốt lõi 2–3 quý liên tiếp; (2) người nội bộ/người nhà liên quan bán lớn đã xác minh, theo ../vnamstock/SKILL.md. Phân biệt đăng ký và kết quả bán; không suy đoán quan hệ. Tách các tín hiệu này với thất bại breakout/tín hiệu kỹ thuật. Nếu xuất hiện xung đột, nêu cả hai; không để điểm CAN SLIM che cảnh báo bán hoặc chờ 2–3 quý mới xem xét tín hiệu kỹ thuật.

## Mẫu báo cáo bắt buộc
1. “BÁO CÁO CAN SLIM — [Mã | Sàn]”, ngày đánh giá, giá tham chiếu/thời gian, phạm vi dữ liệu.
2. Ưu tiên khối Market direction (kết luận) theo nguyên tắc của chuyên gia ở trên; ngay sau đó là Bảng 7 tiêu chí (mục 3), rồi “Minh họa 4 kịch bản” (mục 2b), rồi “Kế hoạch nếu sai”. Báo cáo HTML CAN SLIM KHÔNG có thanh menu/nút điều hướng (Người dùng không cần). Tóm tắt 3–5 câu: chất lượng tăng trưởng, sức mạnh giá, thị trường, trạng thái và dữ liệu thiếu.
2b. **Bắt buộc theo yêu cầu người dùng: “Minh họa 4 kịch bản giao dịch CAN SLIM (giả định)”** ngay sau Bảng 7 tiêu chí (thứ tự: kết luận → Bảng 7 tiêu chí → 4 kịch bản → kế hoạch nếu sai → quý/năm → giá/khối lượng → P/E·PEG → quy tắc của chuyên gia → kiểm định → thuật ngữ → nguồn). Luôn nhận định giả sử điểm mua/bán cho cổ phiếu, kể cả khi chưa có nền giá (khi đó ghi rõ giả định nền và pivot). Vẽ biểu đồ SVG bằng `../vnamstock/scripts/canslim_scenario_chart.py` (giá thực tế ~120 phiên + nền giả định + 3 nhánh tương lai) với 4 mốc: ① điểm mua (pivot → +5% vùng mua, khối lượng ≥1,4–1,5 lần TB50), ② bán cắt lỗ 7–8% từ giá mua, ③ bán chốt lời 20–25% (ngoại lệ +20% trong 3 tuần → giữ ≥8 tuần), ④ bán vì tín hiệu xấu (thủng MA50 với khối lượng lớn, tăng vọt cao trào, thị trường chuyển điều chỉnh, hoặc quy tắc bán bổ sung của chuyên gia). Kèm bảng: kịch bản | điều kiện kích hoạt | mức giá | % so với giá mua | hành động; ghi rõ cách chọn pivot (đỉnh nền/đỉnh nhịp hồi gần nhất + 1 bước giá, hoặc pivot thật nếu có nền đã kiểm chứng). Gắn nhãn nổi bật “minh họa giả định, không phải dự báo”; nhắc chỉ hành động khi điều kiện thật xảy ra và M thuận lợi. Lưu SVG và levels JSON trong `<MA>/CANSLIM/`. Mẫu đã duyệt: `../vnamstock/assets/report-template-CANSLIM-FPT.html`; lưu báo cáo tại `<ROOT>/<MA>/<MA>-VNamStock-CANSLIM-YYYY-MM-DD.html`, không ghi đè bản cũ.
3. Bảng 7 dòng: Tiêu chí | Yêu cầu | Số liệu/bằng chứng | Kỳ/nguồn | Trạng thái | Nhận định.
4. Bảng 4 quý gần nhất: EPS | EPS cùng kỳ | YoY EPS | doanh thu YoY | khoản bất thường. Bảng 4–5 năm: EPS | YoY | doanh thu | ROE | CFO nếu có.
5. Giá/khối lượng và thị trường: benchmark, RS/proxy, MA, 52 tuần, nền giá/pivot có bằng chứng hoặc N/A, điều kiện chờ.
6. P/E/PEG bổ sung; cảnh báo bán của chuyên gia; không tự thêm DCF đầy đủ nếu không cần.
7. Tổng số Đạt/Một phần/Không đạt/Chưa đủ dữ liệu; kết luận có điều kiện, rủi ro và việc cần kiểm tra tiếp.
8. Nguồn: link báo cáo, kỳ, ngày công bố; tách số lịch sử, dự báo và giả định.
Khi so sánh nhiều cổ phiếu, dùng cùng ngày, ngưỡng, cách tính và benchmark phù hợp; không đổi tiêu chí để ưu ái một mã.

## Nguồn phương pháp
- MarketSmith/O'Neil, bảy yếu tố và ngưỡng C/A: https://marketsmith.hk/can-slim-overview/?lang=en
- IBD, công cụ/rating: https://www.investors.com/how-to-invest/how-to-buy-stocks-using-stock-lists-stock-ratings-stock-screener/
- IBD, tham chiếu sức mạnh tương đối: https://www.investors.com/ibd-data-stories/clear-secure-hits-80-plus-relative-strength-rating-benchmark-3/
Tra nguồn phương pháp bổ sung khi khẳng định quy tắc chưa có ở đây. Không dùng tài liệu phương pháp làm nguồn số liệu công ty.



## Kiểm định bắt buộc trước khi trả lời
Đọc và áp dụng ../validation-check/SKILL.md một lần cho mỗi yêu cầu: kiểm tra tiền đề và phạm vi, trích mọi PDF sang text trước khi phân tích, tự tìm dữ liệu công khai còn thiếu, rồi kiểm định kết quả trước khi gửi. Không gọi vòng giữa các skill; chỉ kiểm tra các phần thuộc yêu cầu hiện tại.


## Màu theo dấu của số phần trăm (bắt buộc, từ 11/11/2026)

Trong mọi báo cáo HTML: số % có dấu trừ đứng trước phải là chữ đỏ, có dấu cộng đứng trước phải là chữ xanh — ở mọi chỗ (bảng, ô KPI, đoạn văn, ghi chú), không được để chữ thường. Sau khi viết xong file HTML, luôn chạy `python <SKILLS>/vnamstock/scripts/colorize_signs.py <file.html>` (tự bọc `<span class="sg neg|pos">`, chạy lại nhiều lần vẫn an toàn) rồi mới mở kiểm tra và gửi. Các script dựng báo cáo (`build_report.py`, `hold_plan.py`, `buy_sell_plan.py`, `basic_metrics.py`) đã tự gọi bước này. Số tăng trưởng dương nên viết kèm dấu `+` để được tô xanh.

## Logo doanh nghiệp (bắt buộc, từ 13/11/2026)

Mọi báo cáo HTML về một mã có logo công ty trước tên trong `<h1>` và làm biểu tượng tab trình duyệt (favicon). Báo cáo viết tay: sau bước tô màu dấu, chạy `python <SKILLS>/vnamstock/scripts/add_logo.py <file.html> --ticker <MA> --market vn` (mã Việt Nam lấy logo từ CDN Simplize; mã Mỹ dùng `--market us`, lấy biểu tượng trang web công ty). Logo lưu đệm ở `logo.png` cạnh báo cáo và nhúng base64; chạy lại nhiều lần an toàn. Các script dựng báo cáo (`build_report.py`, `buy_sell_plan.py`, `hold_plan.py`, `basic_metrics.py`) đã tự gắn logo. Không lấy được logo thì vẫn gửi báo cáo, ghi một dòng cho người dùng biết.

## Bảng không được tràn ngang (bắt buộc, từ 11/11/2026)

Mở báo cáo HTML trên máy tính thì mọi bảng phải nằm gọn trong khung, không được có thanh kéo ngang (Người dùng: phải kéo trái/phải rất khó theo dõi). Quy tắc: (1) giữ nguyên khối `THEME: BANG GIA` bản v2 — trong đó ô bảng tự xuống dòng (`th,td{white-space:normal}`) và trang rộng 1200px; không thêm `white-space:nowrap`, `min-width` hay chiều rộng cố định cho bảng/ô, kể cả style viết thẳng trong thẻ; (2) bảng nhiều hơn khoảng 8 cột thì tách thành hai bảng hoặc xoay bảng (chỉ tiêu thành dòng, năm/kịch bản thành cột), rút gọn tiêu đề cột và đưa đơn vị lên tiêu đề (ví dụ "Vốn (tỷ đ)") thay vì lặp trong từng ô; (3) chữ dài để trong cột đầu hoặc ghi chú dưới bảng, không nhồi vào ô số; (4) sau khi tạo file, mở thử ở bề rộng máy tính (1366px và 1024px) và kiểm tra không bảng nào rộng hơn khung chứa nó (`table.scrollWidth <= parentElement.clientWidth`) rồi mới gửi. Trên điện thoại bảng quá nhiều cột vẫn được phép kéo ngang trong khung `.tw`. Cập nhật giao diện cho file cũ: `python <SKILLS>/vnamstock/scripts/apply_theme.py <file hoặc thư mục>`.
