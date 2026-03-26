# TỔNG HỢP NGHIÊN CỨU & ƯU TIÊN TÍNH NĂNG


## StockPulse VN

Nguồn: Ý tưởng sản phẩm · Phân tích cạnh tranh vs FireAnt · Metrics Framework

Ngày: 23/03/2026 | Phiên bản: 1.0 | Nội bộ

## 1. Phương Pháp & Nguồn Nghiên Cứu

Tài liệu này tổng hợp insights từ 3 nguồn nội bộ để xác định và phân loại ưu tiên toàn bộ tính năng của StockPulse VN. Không có dữ liệu người dùng thực — đây là synthesis dựa trên nghiên cứu thị trường và phân tích cạnh tranh.

|                                 |                          |                                                                                   |                                                                       |
| ------------------------------- | ------------------------ | --------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Nguồn nghiên cứu**            | **Loại**                 | **Nội dung cốt lõi**                                                              | **Đóng góp vào synthesis**                                            |
| Ý tưởng ứng dụng (v1.1)         | Product concept          | 5 tính năng chính, tech stack, roadmap 4 giai đoạn, monetization                  | Danh sách đầy đủ tính năng cần đánh giá                               |
| Phân tích cạnh tranh vs FireAnt | Competitive intelligence | FireAnt: 1.3M MAU, AI Copilot, không có Telegram. Khoảng trống thị trường rõ ràng | Bằng chứng về ưu tiên chiến lược, tính năng nào có lợi thế cạnh tranh |
| Metrics Framework (Year 1)      | Product strategy         | North Star: Weekly Engaged Subscribers. OKRs Q1–Q4. Event tracking list           | Xác nhận tính năng nào trực tiếp tác động đến North Star & retention  |

Tiêu chí chấm điểm ưu tiên:

|                                     |              |                                                                |
| ----------------------------------- | ------------ | -------------------------------------------------------------- |
| **Tiêu chí**                        | **Trọng số** | **Cách đánh giá**                                              |
| Tác động đến North Star Metric      | 30%          | Tính năng có trực tiếp tăng Weekly Engaged Subscribers?        |
| Lợi thế cạnh tranh vs FireAnt       | 25%          | FireAnt không có hoặc làm yếu — đây là cơ hội khác biệt?       |
| Tác động đến Activation & Retention | 25%          | Người dùng cần tính năng này để hoàn thành activation event?   |
| Nỗ lực phát triển (đảo ngược)       | 20%          | Tính năng có thể xây dựng nhanh trong MVP hay cần nhiều tháng? |

## 2. Phát Hiện Cốt Lõi — 7 Insights Quan Trọng Nhất

Sau khi cross-reference 3 nguồn, 7 findings sau có bằng chứng mạnh nhất và ảnh hưởng lớn nhất đến quyết định ưu tiên tính năng.

### Finding \#1 — Telegram Bot là khoảng trống lớn nhất trên thị trường

|                     |                                                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                                 |
| Phát hiện           | FireAnt — nền tảng số 1 với 1,3M MAU — hoàn toàn không có Telegram integration. Không một nền tảng chứng khoán VN nào cung cấp trải nghiệm tốt qua Telegram. |
| Bằng chứng          | Competitive brief: 'Không có bằng chứng nào về Telegram bot của FireAnt'. VN có 15M+ người dùng Telegram, phần lớn dùng để theo dõi kênh tài chính.          |
| Tần suất nguồn      | 3/3 nguồn đều nhấn mạnh Telegram là kênh phân phối chính                                                                                                     |
| Tác động kinh doanh | Zero-friction: người dùng không cần cài thêm app. Giảm rào cản acquisition và activation tối đa.                                                             |
| Mức độ tin cậy      | Cao — bằng chứng từ competitive research và product strategy đồng thuận                                                                                      |

### Finding \#2 — Bản tin cá nhân hóa theo watchlist là lõi của retention

|                     |                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                                                    |
| Phát hiện           | North Star Metric (Weekly Engaged Subscribers) phụ thuộc hoàn toàn vào việc người dùng nhận và mở bản tin 3+ lần/tuần. Không có bản tin = không có North Star.                  |
| Bằng chứng          | Metrics Framework: 'North Star = người dùng nhận và mở ít nhất 3 bản tin Telegram trong tuần'. App concept: bản tin sáng 8h + chiều 15h30 được thiết kế là tính năng trung tâm. |
| Tần suất nguồn      | 3/3 nguồn                                                                                                                                                                       |
| Tác động kinh doanh | Trực tiếp tạo thói quen sử dụng hằng ngày — điều kiện tiên quyết cho D7 và D30 retention                                                                                        |
| Mức độ tin cậy      | Cao                                                                                                                                                                             |

### Finding \#3 — AI tóm tắt tin tức với góc nhìn VN là lợi thế có thể xây nhanh

|                     |                                                                                                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                                |
| Phát hiện           | FireAnt có AI Copilot nhưng không chuyên biệt vào việc giải thích 'tại sao sự kiện quốc tế ảnh hưởng VN-Index'. Đây là khoảng trống content có thể lấp đầy. |
| Bằng chứng          | Competitive brief: 'FireAnt có AI nhưng chưa đủ mạnh ở góc độ VN impact analysis'. App concept: tính năng 2.2 Tin tức thế giới ảnh hưởng VN.                |
| Tần suất nguồn      | 2/3 nguồn                                                                                                                                                   |
| Tác động kinh doanh | Tăng giá trị bản tin, tăng open rate, tạo lý do để người dùng không bỏ lỡ bản tin                                                                           |
| Mức độ tin cậy      | Trung bình-Cao                                                                                                                                              |

### Finding \#4 — Cảnh báo giá/RSI là tính năng retention cao nhất ngoài bản tin

|                     |                                                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                            |
| Phát hiện           | Cảnh báo theo ngưỡng (giá, RSI, khối lượng) tạo lý do quay lại app ngẫu nhiên ngoài lịch bản tin. Đây là 'hook' bổ sung để giữ chân người dùng.         |
| Bằng chứng          | Metrics Framework: 'alert\_triggered' và 'alert\_clicked' là events cần track ngay từ ngày 1. App concept: cảnh báo linh hoạt là tính năng của gói Pro. |
| Tần suất nguồn      | 2/3 nguồn                                                                                                                                               |
| Tác động kinh doanh | Tăng DAU/MAU ratio; cảnh báo có giá trị cao là lý do upgrade từ Free lên Pro                                                                            |
| Mức độ tin cậy      | Cao                                                                                                                                                     |

### Finding \#5 — Blog cộng đồng tạo network effect nhưng là khoản đầu tư dài hạn

|                     |                                                                                                                                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                                                                        |
| Phát hiện           | FireAnt có social feed nhưng không có blog phân tích dạng long-form có cấu trúc. Blog cộng đồng tạo SEO organic và giữ chân người dùng — nhưng cần có sẵn nội dung trước khi community tự vận hành. |
| Bằng chứng          | Competitive brief: 'Blog community là cơ hội để tạo network effect mà FireAnt đang thiếu'. App concept: tính năng 2.5 Blog, Giai đoạn 4 (Tháng 7–8).                                                |
| Tần suất nguồn      | 2/3 nguồn                                                                                                                                                                                           |
| Tác động kinh doanh | Tăng thời gian dùng sản phẩm, tạo content SEO, nhưng cần 50+ bài chất lượng trước khi mở cộng đồng                                                                                                  |
| Mức độ tin cậy      | Trung bình — cần validate bằng user interviews                                                                                                                                                      |

### Finding \#6 — Real-time data và mobile app native không phải ưu tiên Year 1

|                     |                                                                                                                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                                                        |
| Phát hiện           | FireAnt đã đầu tư nhiều năm vào real-time data từng giây và mobile app native với 1.3M MAU. Cạnh tranh trực tiếp trên những điểm này sẽ tốn nhiều nguồn lực mà không tạo khác biệt. |
| Bằng chứng          | Competitive brief: 'Gác lại ít nhất 12 tháng đầu: real-time data từng giây, mobile app native'. Metrics Framework: Telegram Bot phục vụ nhu cầu mobile tốt giai đoạn đầu.           |
| Tần suất nguồn      | 2/3 nguồn                                                                                                                                                                           |
| Tác động kinh doanh | Tiết kiệm chi phí phát triển đáng kể; Telegram Bot là native mobile app thay thế trong MVP                                                                                          |
| Mức độ tin cậy      | Cao                                                                                                                                                                                 |

### Finding \#7 — Analytics infrastructure phải build song song với sản phẩm

|                     |                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thuộc tính**      | **Chi tiết**                                                                                                                                      |
| Phát hiện           | Không có event tracking từ ngày 1 = không có dữ liệu để đo North Star Metric. Metrics Framework liệt kê 21 events cần implement trước launch.     |
| Bằng chứng          | Metrics Framework: 'Phải implement event tracking trước launch'. Events quan trọng nhất: newsletter\_opened, onboarding\_completed, bot\_blocked. |
| Tần suất nguồn      | 1/3 nguồn nhưng tác động rất cao                                                                                                                  |
| Tác động kinh doanh | Không đo được = không cải thiện được. Thiếu analytics làm mù tất cả OKRs                                                                          |
| Mức độ tin cậy      | Rất cao — đây là hygiene requirement, không phải feature                                                                                          |

## 3. Phân Khúc Người Dùng Mục Tiêu

Dựa trên synthesis 3 nguồn, StockPulse VN phục vụ 3 phân khúc rõ ràng với nhu cầu khác nhau. Phân khúc 1 là trọng tâm MVP.

|                   |                                                                                           |                                                                                       |                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
|                   | **Phân khúc 1 — Nhà đầu tư bận rộn**                                                      | **Phân khúc 2 — Trader nghiêm túc**                                                   | **Phân khúc 3 — Người mới bắt đầu**                                       |
| Mô tả             | Đầu tư dài hạn, không có thời gian theo dõi thị trường liên tục. Dùng Telegram hằng ngày. | Giao dịch thường xuyên, cần tín hiệu kỹ thuật và cảnh báo real-time. Đã quen FireAnt. | Mới tham gia thị trường, cần hướng dẫn và nội dung giáo dục đơn giản.     |
| Quy mô ước tính   | 60% người dùng mục tiêu                                                                   | 25% người dùng mục tiêu                                                               | 15% người dùng mục tiêu                                                   |
| Nhu cầu cốt lõi   | Bản tin tóm tắt hằng ngày, không cần mở app. Cảnh báo khi cổ phiếu đạt mức quan tâm.      | Cảnh báo RSI, MACD tức thời. Phân tích kỹ thuật đủ tốt để thay FireAnt.               | Blog giáo dục, giải thích đơn giản về chỉ số, không có biệt ngữ phức tạp. |
| Tính năng ưu tiên | Bot Telegram, newsletter, cảnh báo giá                                                    | Cảnh báo RSI/MACD, phân tích kỹ thuật, Pro subscription                               | Blog hướng dẫn, onboarding rõ ràng, watchlist đơn giản                    |
| Gói tiềm năng     | Free → Pro (99K/tháng)                                                                    | Pro → Premium (299K/tháng)                                                            | Free (chủ yếu)                                                            |
| Rủi ro churn      | Thấp nếu bản tin có giá trị cao                                                           | Cao nếu dữ liệu không đủ real-time                                                    | Cao nếu sản phẩm quá phức tạp                                             |

## 4. Ma Trận Ưu Tiên Tính Năng — Toàn Bộ Backlog

Tổng cộng 28 tính năng được phân loại theo 5 mức ưu tiên. Mỗi tính năng được đánh giá dựa trên 4 tiêu chí: tác động North Star, lợi thế cạnh tranh, tác động retention, và nỗ lực phát triển.

**Hướng dẫn đọc:**

  - Điểm tổng: tính theo trọng số đã định ở Mục 1 (tối đa 10 điểm)

  - North Star Impact: tính năng trực tiếp tăng Weekly Engaged Subscribers

  - Competitive Edge: FireAnt không có hoặc làm yếu tính năng này

  - Effort: 1 = cần nhiều tháng, 5 = có thể build trong 1–2 tuần

### P0 – PHẢI CÓ TRƯỚC LAUNCH (Blockers)

> *Không có những tính năng này thì sản phẩm không thể vận hành. Phải xong trước ngày ra mắt.*

|                             |                                                                                 |                       |                      |               |                  |
| --------------------------- | ------------------------------------------------------------------------------- | --------------------- | -------------------- | ------------- | ---------------- |
| **Tính năng**               | **Mô tả**                                                                       | **North Star Impact** | **Competitive Edge** | **Điểm Tổng** | **Effort (1–5)** |
| Telegram Bot – Onboarding   | Lệnh /start, hướng dẫn thiết lập, liên kết tài khoản Google                     | Rất cao               | Cao                  | 9,5           | 3                |
| Thiết lập Watchlist qua Bot | Người dùng thêm/xoá tối đa 3 mã (Free) hoặc 10 mã (Pro) qua Telegram            | Rất cao               | Cao                  | 9,2           | 3                |
| Bản tin buổi sáng (8:00)    | Tự động gửi bản tin tổng quan thị trường + watchlist hằng ngày                  | Rất cao               | Rất cao              | 9,8           | 4                |
| Google OAuth Login          | Đăng nhập / đăng ký bằng Google — không cần mật khẩu riêng                      | Cao                   | Trung bình           | 8,0           | 3                |
| Analytics & Event Tracking  | Implement 21 events (newsletter\_opened, onboarding\_completed…) ngay từ ngày 1 | Rất cao               | Trung bình           | 8,5           | 2                |
| Database Schema cơ bản      | Users, watchlists, subscriptions, notification\_logs                            | Cao                   | Thấp                 | 7,5           | 3                |

### P1 – ƯU TIÊN CAO (Months 1–3 sau Launch)

> *Cần có để hoàn thiện core value loop và bắt đầu monetization. Build ngay sau khi P0 ổn định.*

|                                                |                                                                                                     |                       |                      |               |                  |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------- | -------------------- | ------------- | ---------------- |
| **Tính năng**                                  | **Mô tả**                                                                                           | **North Star Impact** | **Competitive Edge** | **Điểm Tổng** | **Effort (1–5)** |
| Bản tin buổi chiều (15:30)                     | Tổng kết kết phiên giao dịch + nhận định + top gainers/losers                                       | Cao                   | Rất cao              | 9,0           | 2                |
| AI tóm tắt tin tức + đánh giá tác động VN      | Dùng AI (OpenAI/Gemini) đánh giá tin quốc tế tác động VN-Index: tích cực/tiêu cực/trung lập + lý do | Cao                   | Rất cao              | 9,1           | 4                |
| Cảnh báo giá theo ngưỡng tùy chỉnh             | Notify khi VCB \> 95,000 hoặc \< 88,000 — real-time qua Telegram                                    | Cao                   | Cao                  | 8,8           | 3                |
| VN-Index / HNX / UPCOM tổng quan trong bản tin | Điểm số, % thay đổi, KLGD, so sánh 20 phiên                                                         | Cao                   | Trung bình           | 8,2           | 2                |
| Top 5 tăng/giảm mạnh nhất trong ngày           | Hiển thị trong bản tin hằng ngày với % thay đổi và lý do ngắn gọn                                   | Cao                   | Trung bình           | 8,0           | 2                |
| Khối ngoại mua/bán ròng                        | Top cổ phiếu được khối ngoại mua/bán nhiều nhất — signal quan trọng                                 | Trung bình            | Cao                  | 7,8           | 2                |
| Pro Subscription + Payment (99K/tháng)         | Tích hợp thanh toán (Stripe hoặc PayOS), unlock watchlist 10 mã và cảnh báo real-time               | Trung bình            | Trung bình           | 7,5           | 4                |

### P2 – QUAN TRỌNG (Months 3–6)

> *Tăng giá trị sản phẩm, cải thiện retention, mở rộng cơ hội monetization.*

|                                                   |                                                                           |                       |                      |               |                  |
| ------------------------------------------------- | ------------------------------------------------------------------------- | --------------------- | -------------------- | ------------- | ---------------- |
| **Tính năng**                                     | **Mô tả**                                                                 | **North Star Impact** | **Competitive Edge** | **Điểm Tổng** | **Effort (1–5)** |
| Cảnh báo RSI quá mua/quá bán                      | Notify khi RSI \< 30 hoặc \> 70 cho các mã trong watchlist                | Trung bình            | Cao                  | 7,8           | 3                |
| Cảnh báo đột biến khối lượng (\>200% TB)          | Phát hiện bất thường KLGD — tín hiệu sớm của biến động                    | Trung bình            | Cao                  | 7,6           | 3                |
| Sự kiện doanh nghiệp (ĐHCĐ, cổ tức, niêm yết mới) | Lịch sự kiện tự động nhắc trong bản tin theo mã watchlist                 | Trung bình            | Cao                  | 7,5           | 3                |
| Phân tích kỹ thuật cơ bản (MA20/50/200)           | Hiện trạng MA so với giá đóng cửa cho từng mã watchlist trong bản tin     | Trung bình            | Trung bình           | 7,0           | 3                |
| Tin tức quốc tế có ảnh hưởng VN (Fed, dầu, vàng)  | Theo dõi và lọc tự động các chỉ số: VIX, USD/VND, giá dầu Brent, S\&P 500 | Trung bình            | Cao                  | 7,4           | 3                |
| Web Dashboard cơ bản                              | Trang cài đặt watchlist, lịch sử bản tin, tài khoản người dùng            | Thấp                  | Thấp                 | 6,0           | 4                |
| Premium Subscription (299K/tháng)                 | Unlock phân tích chuyên sâu, không giới hạn mã, ưu tiên support           | Thấp                  | Trung bình           | 6,5           | 2                |

### P3 – NÊN CÓ (Months 6–9)

> *Tính năng tạo khác biệt dài hạn và network effect, nhưng không phải điều kiện để có user đầu tiên.*

|                                               |                                                                               |                       |                      |               |                  |
| --------------------------------------------- | ----------------------------------------------------------------------------- | --------------------- | -------------------- | ------------- | ---------------- |
| **Tính năng**                                 | **Mô tả**                                                                     | **North Star Impact** | **Competitive Edge** | **Điểm Tổng** | **Effort (1–5)** |
| Blog chính thức – CMS cho admin/biên tập viên | Trình soạn thảo rich text, quản lý bài viết, lên lịch xuất bản, gắn tag mã CK | Trung bình            | Cao                  | 7,2           | 4                |
| Liên kết blog → bản tin Telegram              | Tự động đính kèm link bài blog nổi bật vào bản tin buổi sáng                  | Cao                   | Rất cao              | 7,8           | 2                |
| Trang chi tiết mã cổ phiếu                    | Tổng hợp: giá hiện tại, chỉ báo kỹ thuật, tin tức liên quan, bài blog theo mã | Trung bình            | Trung bình           | 6,5           | 4                |
| NPS Survey & CSAT automation                  | Tự động gửi khảo sát NPS qua bot sau 30 ngày sử dụng                          | Thấp                  | Thấp                 | 5,8           | 2                |
| Referral program                              | Người dùng nhận thêm 1 mã watchlist khi giới thiệu bạn bè thành công          | Trung bình            | Trung bình           | 6,2           | 3                |

### P4 – BACKLOG (Month 9+)

> *Tính năng có giá trị nhưng không nên đầu tư trong năm đầu. Xem xét lại sau khi có 5,000+ Weekly Engaged Subscribers.*

|                                           |                                                                          |                                                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **Tính năng**                             | **Mô tả**                                                                | **Lý do defer**                                                                                            |
| Blog cộng đồng (user-generated)           | Người dùng đăng bài phân tích cá nhân với hệ thống kiểm duyệt            | Cần official blog có nội dung chất lượng trước; community cần tối thiểu 2,000 active users mới tự vận hành |
| Like / Comment / Follow tác giả           | Tương tác cộng đồng trên blog: like, bình luận, theo dõi tác giả         | Phụ thuộc community blog (P4 trên)                                                                         |
| Full-text search bài viết theo mã CK      | Tìm kiếm bài phân tích theo ticker (VD: tìm tất cả bài về VCB)           | Chỉ có giá trị khi có 50+ bài blog                                                                         |
| Phân tích kỹ thuật nâng cao (50+ chỉ báo) | Biểu đồ TradingView full với Bollinger Bands, Fibonacci, Volume Profile… | FireAnt đã rất mạnh; cạnh tranh trực tiếp tốn nguồn lực nhưng không phải điểm khác biệt                    |
| Mobile App native (iOS/Android)           | Ứng dụng di động độc lập ngoài Telegram                                  | Telegram Bot thay thế tốt trong giai đoạn đầu với chi phí bằng 0                                           |
| AI Copilot tương tác (chat với AI)        | Chatbot AI tư vấn đầu tư theo ngữ cảnh                                   | FireAnt đã có; cần 6–12 tháng để build tốt hơn; không phải lợi thế cạnh tranh                              |
| Tích hợp AmiBroker/MetaStock              | Export dữ liệu cho nhà đầu tư dùng phần mềm chuyên nghiệp                | Phân khúc hẹp, phức tạp, FireAnt đã có                                                                     |

## 5. Đánh Giá Cơ Hội – Top 5 Tính Năng Có ROI Cao Nhất

Ước tính tác động của 5 tính năng quan trọng nhất lên North Star Metric và MRR. Số liệu dựa trên benchmark ngành và assumptions thận trọng.

|                                    |                                                                                                                 |                                                                          |                                                                           |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| **Tính năng**                      | **Cơ chế tác động**                                                                                             | **Ước tính tác động North Star**                                         | **Ước tính tác động MRR**                                                 |
| Telegram Bot + Bản tin sáng        | Mỗi subscriber nhận bản tin → nếu mở 3+/tuần = 1 Weekly Engaged Subscriber. Đây là tính năng tạo ra North Star. | \= 100% North Star Metric. Không có tính năng này = North Star = 0.      | Gián tiếp: retention cao hơn → conversion Free→Pro cao hơn                |
| AI tóm tắt tin tức VN-impact       | Open rate tăng khi nội dung có giá trị cao hơn. Ước tính tăng open rate từ 45% → 58%.                           | \+29% Weekly Engaged Subscribers (từ 500 → 645 ở M3 nếu open rate tăng). | Là lý do chính để upgrade Pro — feature có thể lock sau Free tier         |
| Cảnh báo giá + RSI                 | Người dùng quay lại app ngoài lịch bản tin. Tăng DAU/MAU từ 0,30 → 0,42.                                        | \+40% DAU/MAU stickiness. Người dùng có alert click 2× ít churn hơn.     | Feature chính của gói Pro — ước tính 40% lý do upgrade                    |
| Pro Subscription (99K/tháng)       | Tạo doanh thu trực tiếp. Target 3% conversion ở M3 (= 15 paid users / 500 subscribers).                         | Neutral — không trực tiếp tăng North Star                                | 15 users × 99K = \~1,5M VND/tháng ở M3. 60 users × 99K = \~6M VND ở M6.   |
| Blog chính thức + liên kết bản tin | Tăng giá trị bản tin (có link đọc thêm), tăng time-on-product, tạo SEO organic.                                 | \+15% organic new subscribers qua Google search sau 3 tháng.             | Gián tiếp: tăng acquisition → nhiều subscriber hơn → nhiều conversion hơn |

## 6. Trình Tự Phát Triển Đề Xuất

> *Nguyên tắc: Xây những thứ tạo ra North Star Metric trước. Đừng build tính năng 'nice to have' trước khi validate tính năng cốt lõi.*

|                       |               |                                                                                                        |                                                                   |
| --------------------- | ------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **Giai đoạn**         | **Thời gian** | **Tính năng cần hoàn thành**                                                                           | **Mục tiêu đo lường**                                             |
| Sprint 0 — Foundation | Tuần 1–2      | Database schema, Google OAuth, Telegram Bot /start, Analytics events setup                             | Bot hoạt động ổn định; có thể track newsletter\_opened            |
| Sprint 1 — Core Loop  | Tuần 3–5      | Bản tin sáng 8h tự động, Watchlist setup (3 mã), VN-Index overview trong bản tin, Top 5 gainers/losers | Gửi được bản tin cho 10 beta users. Open rate \> 50%.             |
| Sprint 2 — Value Add  | Tuần 6–8      | Bản tin chiều 15h30, Cảnh báo giá, AI tóm tắt tin tức + VN-impact, Khối ngoại                          | Activation rate \> 40%. Open rate \> 45%.                         |
| Sprint 3 — Monetize   | Tuần 9–11     | Pro subscription (99K/tháng) + PayOS, Watchlist nâng lên 10 mã cho Pro, RSI alerts cho Pro             | First revenue. Free→Pro conversion \> 2%.                         |
| Sprint 4 — Grow       | Tuần 12–16    | Referral program, Sự kiện doanh nghiệp (ĐHCĐ/cổ tức), Web dashboard cơ bản, Premium (299K/tháng)       | Weekly Engaged Subscribers \> 500. MRR \> 5M VND.                 |
| Sprint 5 — Content    | Tháng 5–6     | Blog chính thức (CMS), 20 bài viết phân tích chất lượng cao, Liên kết blog → bản tin                   | Blog → newsletter CTR \> 15%. Organic traffic bắt đầu tăng.       |
| Sprint 6 — Community  | Tháng 7–8     | Blog cộng đồng (user-generated), Hệ thống kiểm duyệt, Like/comment/follow                              | 50 bài user-generated/tháng. Weekly Engaged Subscribers \> 2,000. |

## 7. Câu Hỏi Còn Mở — Cần Validate Trước Khi Quyết Định

Những câu hỏi này không thể trả lời bằng research hiện tại — cần user interviews hoặc A/B testing sau launch.

|                                                                                  |                                                                                                                    |                                                                                                          |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **Câu hỏi**                                                                      | **Tại sao quan trọng**                                                                                             | **Cách validate**                                                                                        |
| Người dùng muốn bản tin buổi sáng hay buổi chiều hơn? Hay cả hai?                | Nếu mở rate buổi chiều thấp hơn nhiều, có thể tập trung vào 1 bản tin chất lượng cao thay vì 2 bản tin trung bình. | A/B test sau 200 subscribers: group A nhận cả 2, group B chỉ nhận buổi sáng. So sánh open rate và churn. |
| Người dùng Free có chuyển đổi sang Pro vì cảnh báo giá hay vì watchlist 10 mã?   | Quyết định tính năng nào là 'paywall' chính của Pro tier.                                                          | Survey người dùng Pro sau khi upgrade: 'Tính năng nào thuyết phục bạn upgrade?'                          |
| Blog có phải là lý do người dùng ở lại, hay chỉ là nice-to-have?                 | Nếu blog không tác động retention, có thể defer sang năm 2.                                                        | So sánh D30 retention của user đọc blog vs user chưa bao giờ đọc blog.                                   |
| Người dùng muốn nhận bản tin lúc mấy giờ?                                        | Thời điểm gửi ảnh hưởng trực tiếp đến open rate.                                                                   | Cho phép user chọn giờ nhận tin trong onboarding, track open rate theo từng khung giờ.                   |
| Ai là kênh acquisition hiệu quả nhất: Facebook groups chứng khoán, KOL, hay SEO? | Xác định nơi tập trung ngân sách marketing giai đoạn đầu.                                                          | Chạy thử 3 kênh với budget nhỏ (1M VND/kênh), so sánh CPS (cost per subscriber).                         |

*Tài liệu này là research synthesis dựa trên phân tích thị trường và tài liệu nội bộ, không phải dữ liệu người dùng thực. Tất cả điểm số ưu tiên là ước tính định tính. Cần validate bằng user interviews và A/B testing sau khi ra mắt MVP.*
