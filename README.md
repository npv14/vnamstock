# VNamStock — trợ lý phân tích cổ phiếu Việt Nam cho Claude Code

VNamStock là bộ skill cho [Claude Code](https://claude.com/claude-code). Bạn chỉ cần gõ một câu tiếng Việt, ví dụ *"định giá FPT"*. Claude sẽ tự lấy báo cáo tài chính từ CafeF, tính toán bằng Python và xuất **báo cáo HTML tiếng Việt** (đọc được trên điện thoại, có chế độ tối). Thuật ngữ được giải thích ngay dưới mỗi phần.

> ⚠️ **Không phải tư vấn đầu tư.** Đây là công cụ phân tích theo khung quy tắc tổng hợp từ chuyên gia. Mọi con số dựa trên dữ liệu công khai và giả định có thể sai. Bạn tự chịu trách nhiệm với quyết định của mình. Công cụ không đặt lệnh giao dịch.

## Có gì bên trong

| Skill | Gõ thử | Kết quả |
|---|---|---|
| `vnamstock` | "VNamStock phân tích HPG" | Skill chính: quy trình, hai quy tắc bán, giải thích thuật ngữ |
| `vnamstock-full-report` | "báo cáo tổng hợp FPT" | Định giá NCAV, DCF 10 năm, Owner Earnings × 3 kịch bản + giá mua theo biên an toàn → phân tích cơ bản 5 năm + 5 kịch bản giá → chi tiết định giá |
| `vnamstock-buy-sell-plan` | "kế hoạch mua bán FPT, 1.000 cp giá 60.000, định bán 100.000" | Lãi kép từ cổ tức khi giữ 5–10 năm, mua thêm, tỷ lệ Kelly |
| `canslim-report` | "chấm CAN SLIM MWG" | 7 tiêu chí CAN SLIM, 4 kịch bản mua/bán, mức cắt lỗ |
| `four-m-report` | "phân tích 4M VNM" | 4M của Phil Town + lãi suất, chu kỳ, thời điểm mua tích trữ |
| `validation-check` | (tự chạy) | Kiểm tra số liệu và kết quả trước khi trả lời |

**Hai quy tắc bán của chuyên gia** được kiểm tra trong mọi báo cáo:
1. Lợi nhuận không tăng trưởng so với cùng kỳ trong 2–3 quý liên tiếp.
2. Lãnh đạo hoặc người nội bộ bán nhiều cổ phiếu.

Mẫu báo cáo nằm trong `skills/*/assets/`. Mở file `.html` bằng trình duyệt để xem.

## Cài đặt

**Cần có:** Claude Code (bản app hoặc dòng lệnh) và Python 3.9 trở lên.

**Bước 1 — Cài plugin.** Gõ trong Claude Code:

```
/plugin marketplace add npv14/vnamstock
```

```
/plugin install vnamstock@vnamstock
```

**Bước 2 — Cài thư viện Python** (một lần):

```bash
pip install -r requirements.txt
```

Nếu đã cài plugin mà không tìm thấy file này, chạy thẳng:

```bash
pip install requests openpyxl tzdata
```

**Bước 3 — Chọn thư mục làm việc.** Tạo một thư mục riêng, ví dụ `Documents/VNStock`, rồi mở Claude Code ở đó. Mọi dữ liệu và báo cáo sẽ lưu theo mã, ví dụ `FPT/FPT-VNamStock-TongHop-2026-11-07.html`. Muốn dùng thư mục cố định, đặt biến môi trường `VNAMSTOCK_ROOT`.

**Bước 4 — Thử:** gõ *"báo cáo tổng hợp FPT"*.

### Prompt cài nhanh cho người mới

Dán vào Claude Code:

```text
Cài plugin VNamStock từ GitHub cho mình:
1. Chạy /plugin marketplace add npv14/vnamstock rồi /plugin install vnamstock@vnamstock
   (nếu bạn không tự chạy được lệnh /plugin thì hướng dẫn mình gõ).
2. Kiểm tra Python 3.9+ và cài: pip install requests openpyxl tzdata
3. Hỏi mình muốn lưu báo cáo ở thư mục nào.
4. Chạy thử "báo cáo tổng hợp FPT" và gửi mình đường dẫn file HTML.
Không cài gì khác ngoài những thứ trên.
```

## Cập nhật và gỡ

- Cập nhật: `/plugin marketplace update vnamstock`
- Gỡ: `/plugin uninstall vnamstock@vnamstock`

## Nguồn dữ liệu và giới hạn

- Báo cáo tài chính, giá và giao dịch nội bộ lấy từ các trang công khai của **CafeF** (không cần tài khoản hay khóa API). CafeF có thể đổi cấu trúc bất cứ lúc nào, nên script có thể ngừng chạy. Khi đó Claude sẽ báo phần thiếu.
- Hiện chỉ hỗ trợ cổ phiếu niêm yết ở Việt Nam (HOSE, HNX, UPCoM).
- Ngân hàng và bảo hiểm cần phương pháp định giá riêng. Báo cáo sẽ ghi rõ khi một phương pháp không phù hợp.
- Số liệu trong file mẫu là ví dụ tại thời điểm lập. Không dùng chúng để ra quyết định.

## Giấy phép

[MIT](LICENSE): bạn được dùng, sửa và chia sẻ tự do, kể cả cho mục đích thương mại, miễn giữ lại thông báo bản quyền.
