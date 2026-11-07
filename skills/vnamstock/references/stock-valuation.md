# Stock Valuation from Image

Version: 1.2.1

Đọc `valuation-rules.md` trước khi tính toán; các quy tắc 1.2 trong đó thay thế công thức cũ nếu có xung đột.

## Trigger
Khi người dùng gửi ảnh chỉ số cổ phiếu và yêu cầu phân tích, định giá, intrinsic value, DCF, Owner Earnings, Net Working Capital, NCAV hoặc margin of safety, payback time hoặc thời gian hoàn vốn. Trả lời bằng tiếng Việt trừ khi người dùng yêu cầu ngôn ngữ khác.

## Workflow
1. Đọc ảnh bằng khả năng thị giác, nhận diện mã chứng khoán, sàn, đơn vị tiền, ngày số liệu, giá, số cổ phiếu, EPS, P/E, P/B, BVPS, ROE, ROA, ROS, GOS, DAR. Ghi nguồn là 'ảnh người dùng' và nêu các mục không đọc rõ. Không tự bịa dữ liệu thiếu.
2. Kiểm tra các chỉ số có khớp không: P/E≈giá/EPS; P/B≈giá/BVPS. Chú ý chia tách/cổ tức cổ phiếu, cổ phiếu bình quân vs cuối kỳ, lợi nhuận cổ đông mẹ, báo cáo hợp nhất, đơn vị tỷ/triệu/nghìn, dữ liệu trailing vs năm tài chính. Nếu mâu thuẫn, ghi rõ và không sử dụng số sai làm cơ sở.
3. Chủ động tìm báo cáo tài chính và công bố mới nhất từ nguồn chính thức (IR công ty, HOSE/HNX, báo cáo kiểm toán); trích nguồn và ngày kỳ báo cáo. Thu thập tài sản ngắn hạn, nợ ngắn hạn, tổng nợ phải trả, tiền và đầu tư thanh khoản, nợ vay có lãi, cổ đông thiểu số, CFO, CAPEX, D&A, thay đổi vốn lưu động, lợi nhuận thuộc cổ đông mẹ, số cổ phiếu pha loãng. Nếu không có nguồn, yêu cầu người dùng bổ sung ảnh bảng cân đối và lưu chuyển tiền tệ; có thể đưa minh họa nhưng gắn nhãn giả định.
4. Phương pháp 1 — NWC = tài sản ngắn hạn - nợ ngắn hạn. NCAV = tài sản ngắn hạn - tổng nợ phải trả; NCAV/cp = NCAV / số cổ phiếu phù hợp. Ngưỡng Graham 2/3 NCAV/cp nếu NCAV dương. NWC là thước đo thanh khoản, KHÔNG phải intrinsic value. Nếu NCAV âm, không coi ngưỡng 2/3 là giá mua. Giải thích giới hạn với doanh nghiệp asset-light.
5. Phương pháp 2 — DCF chuẩn: ưu tiên FCFF = EBIT*(1-T)+D&A-CAPEX-ΔNWC hoạt động; chiết khấu bằng WACC; terminal value = FCFF_(n+1)/(WACC-g); EV = PV FCFF + PV terminal; equity value = EV + tiền dư thừa - nợ vay có lãi - lợi ích cổ đông thiểu số + tài sản phi hoạt động (nếu thích hợp); chia cổ phiếu pha loãng. Hoặc FCFE chiết khấu bằng cost of equity và KHÔNG cộng lại tiền ròng một cách trùng lặp. Không pha trộn FCFF/FCFE với discount rate hoặc cộng tiền ròng không nhất quán. Chuẩn hóa FCF bất thường, vốn lưu động, thay đổi hợp nhất. Dự phóng 10 năm; dùng tăng trưởng giảm dần về g dài hạn hợp lý; đảm bảo WACC>g.
6. Phương pháp 3 — Owner Earnings = lợi nhuận thuộc chủ sở hữu + D&A và điều chỉnh phi tiền mặt - CAPEX duy trì - nhu cầu vốn lưu động duy trì, xử lý khoản bất thường và lợi ích cổ đông thiểu số. Không tự khẳng định CAPEX tăng trưởng/duy trì nếu chưa có thuyết minh; xây ba giả định minh bạch, đối chiếu với CFO-CAPEX. Định giá bằng chiết khấu Owner Earnings cho cổ đông với cost of equity, không cộng tiền ròng trùng lặp; nêu giả định về nợ và tiền. Nếu thiếu CAPEX duy trì, trình bày khoảng định giá có điều kiện, không kết luận giá trị chính xác.
7. Mỗi phương pháp tính 3 kịch bản bear/base/bull, thể hiện tham số: base cash flow, tốc độ tăng trưởng, chiết khấu, terminal growth, cổ phiếu, điều chỉnh nợ/tiền, nguồn. Tính giá/cp, upside/downside = value/market price-1; margin of safety = 1-market price/value khi value>0; giá mua ở MOS 15%, 25%, 30%, 50% = intrinsic value*(1-MOS). Nêu sensitivity với WACC và tăng trưởng, không trình bày các ngưỡng như đảm bảo.
8. Bắt buộc kiểm tra thời gian hoàn vốn (Payback Time) cho cả FCF/FCFE phù hợp và Owner Earnings, với CÙNG giả định tăng trưởng khi so sánh. Tính trên mỗi cổ phiếu: CF0/cp = dòng tiền thuộc cổ đông phổ thông / số cổ phiếu pha loãng; P0 là giá thị trường/cp tại ngày tham chiếu. Nếu CF0<=0, không báo số năm hoàn vốn bằng phép chia; giải thích vì sao. Phân biệt:
   - Simple payback không tăng trưởng = P0 / CF0/cp (chỉ hợp lệ với dòng tiền dương, ổn định).
   - Growing payback không chiết khấu: tìm năm nguyên nhỏ nhất N sao cho Σ(t=1..N) CF_t với CF_t = CF_(t-1)*(1+g_t) >= P0. Cho biết năm vượt ngưỡng, có thể nội suy trong năm và ghi rõ chỉ là xấp xỉ. Nếu dòng tiền năm 1 bằng CF0 thay vì CF0*(1+g), phải công bố quy ước và dùng nhất quán.
   - Discounted payback: tìm năm đầu tiên Σ(t=1..N) CF_t/(1+r)^t >= P0, với r là cost of equity thích hợp cho dòng tiền thuộc cổ đông. Nếu không đạt trong kỳ dự phóng, ghi 'chưa hoàn vốn trong N năm', KHÔNG cộng terminal value hoặc giá bán giả định để gọi là hoàn vốn từ dòng tiền hoạt động. Nếu tăng trưởng g<r vĩnh viễn và PV toàn bộ dòng tiền <= P0, ghi 'không hoàn vốn chiết khấu theo giả định này'.
   - Nếu sử dụng FCFF doanh nghiệp, KHÔNG so trực tiếp FCFF/cp với giá cổ phiếu; phải chuyển sang FCFE hoặc dòng tiền có thể phân phối thuộc cổ đông trước khi tính payback giá cổ phiếu.
   - Thời gian hoàn vốn kinh tế không đồng nghĩa tiền cổ tức thực nhận, không tính lợi nhuận do bán cổ phiếu và không phải bản thân DCF. Luôn so sánh ít nhất 0%, tăng trưởng cơ sở và tăng trưởng người dùng yêu cầu (ví dụ 13%), với số liệu và nguồn rõ ràng. Tăng trưởng lợi nhuận báo cáo 13% KHÔNG mặc nhiên là tăng trưởng FCF hoặc Owner Earnings 13% trong 10 năm. Dùng dự phóng từng năm, kiểm tra kết quả số học; không dùng P0/CF0 khi có tăng trưởng rồi gọi đó là payback tăng trưởng.
9. So sánh ba phương pháp và giải thích tại sao chênh lệch; ưu tiên tính phù hợp với mô hình kinh doanh hơn là lấy trung bình máy móc. Kết luận phân biệt: sức khỏe tài chính, giá trị ước tính, mức độ tin cậy, rủi ro, dữ liệu cần xác minh. Không đưa lời khuyên mua chắc chắn hoặc cam kết lợi nhuận.

## P/E, PEG và chất lượng tăng trưởng — bắt buộc
Mỗi khi phân tích cổ phiếu có P/E, chủ động nhấn mạnh PEG ngay cạnh P/E, kể cả người dùng không hỏi riêng PEG. Giải thích P/E trong tương quan với tốc độ và chất lượng tăng trưởng EPS, không đánh giá rẻ/đắt chỉ từ P/E.
- Tính PEG = P/E / tốc độ tăng trưởng EPS hằng năm tính bằng số phần trăm: P/E 20, tăng trưởng EPS 15% thì PEG=20/15≈1,33; không chia cho 0,15.
- Ghi rõ P/E trailing hay forward, kỳ EPS, thời điểm giá, nguồn và kỳ tăng trưởng. Ưu tiên tăng trưởng EPS dự kiến bình quân 3–5 năm có nguồn đáng tin; nếu chỉ có lịch sử, dùng CAGR EPS 3–5 năm có dữ liệu và ghi “PEG theo tăng trưởng lịch sử”. Không gộp các cơ sở kỳ khác nhau khi so sánh. CAGR=(EPS cuối/EPS đầu)^(1/số năm)-1 chỉ dùng khi EPS đầu/cuối dương và chuỗi không có biến động dấu khiến chỉ tiêu gây hiểu nhầm.
- Không dùng tăng trưởng doanh thu hoặc tổng lợi nhuận thay cho EPS mà không công bố rõ phép xấp xỉ và hạn chế do pha loãng; không tự coi tăng trưởng một quý/một năm là tăng trưởng dài hạn. Điều chỉnh chia tách/cổ tức cổ phiếu và lợi nhuận bất thường nhất quán.
- Nếu EPS/P/E không dương, tăng trưởng EPS ≤0 hoặc thiếu dữ liệu đáng tin: ghi PEG “không có ý nghĩa/không đủ dữ liệu”, giải thích và tiếp tục đánh giá tăng trưởng; không bịa tỷ lệ hoặc diễn giải PEG âm là rẻ.
- Trình bày PEG <1, ≈1, >1 chỉ như tham khảo tương quan giá/tăng trưởng, không phải ngưỡng mua/bán hay giá trị hợp lý tuyệt đối. Xét ngành, chu kỳ, rủi ro, lãi suất, cổ tức và chất lượng dự báo; đặc biệt cảnh giác nền lợi nhuận thấp và doanh nghiệp bất động sản ghi nhận theo đợt.
- Đánh giá công ty đang phát triển thế nào: xu hướng doanh thu, EPS, biên lợi nhuận, ROE/ROIC, chuyển đổi lợi nhuận thành CFO/FCF, nợ và pha loãng; phân biệt tăng trưởng kinh doanh cốt lõi với khoản một lần/mua lại cổ phiếu. Nêu động lực, tính bền vững, tăng tốc/chậm lại và dữ liệu còn thiếu.
- Xuất bảng P/E | loại/kỳ P/E | tăng trưởng EPS và kỳ | lịch sử/dự báo | PEG | nguồn/độ tin cậy, rồi nhận định ngắn về chất lượng tăng trưởng. Không tự dùng tăng trưởng EPS làm tăng trưởng FCF/OE cho DCF hoặc payback.

## Output format
- Tên mã, ngày định giá, giá và thời điểm tham chiếu, nguồn.
- Bảng chỉ số trích từ ảnh, cảnh báo không nhất quán.
- Bảng NWC/NCAV (đơn vị và trên mỗi cổ phiếu).
- Bảng DCF 3 kịch bản, tham số và giá trị/cp.
- Bảng Owner Earnings 3 kịch bản, phân biệt maintenance CAPEX giả định.
- Bảng so sánh 3 phương pháp với giá thị trường, upside/downside và MOS.
- Bảng Payback Period: FCF/FCFE và Owner Earnings, dòng tiền/cp ban đầu, tăng trưởng, simple payback, growing payback và discounted payback; ghi rõ trường hợp chưa hoàn vốn và các giả định.
- Kết luận ngắn: mức độ tin cậy, yếu tố có thể làm thay đổi định giá, dữ liệu còn thiếu.

## Quality rules
Không suy diễn CFO, CAPEX, số cổ phiếu, nợ vay, tiền mặt từ P/E/ROE. Không dùng giá cũ như giá hiện tại mà không ghi rõ. Không gọi simple payback là DCF; không so sánh hai payback khi dùng giả định tăng trưởng khác nhau mà không giải thích. Không nhầm NWC với NCAV. Không nhầm tổng nợ phải trả với nợ vay có lãi. Kiểm tra đơn vị và công thức bằng tính toán khi có thể. Trích dẫn báo cáo, không bịa nguồn. Nếu chỉ có ảnh chỉ số cơ bản, bắt đầu bằng phân tích các số đã có và nói rõ cần thêm báo cáo tài chính cho định giá 3 phương pháp đáng tin cậy.
