# 📈 Ý Tưởng Xây Dựng Ứng Dụng Chứng Khoán Thông Minh
> **Người tư vấn:** AI Financial Consultant
> **Ngày lập:** 23/03/2026
> **Phiên bản:** 1.0

---

## 1. Tổng Quan Sản Phẩm

**Tên ứng dụng đề xuất:** **StockPulse VN** — Nền tảng thông tin & phân tích chứng khoán cá nhân hóa, tích hợp cảnh báo thông minh qua Telegram.

**Mục tiêu cốt lõi:** Giúp nhà đầu tư cá nhân tại Việt Nam tiếp cận thông tin thị trường nhanh chóng, chính xác và được phân tích tự động — mọi lúc, mọi nơi, ngay trên Telegram.

---

## 2. Tính Năng Chính

### 2.1. 📬 Bản Tin Chứng Khoán Việt Nam Hằng Ngày (qua Telegram)

**Mô tả:** Mỗi ngày, hệ thống tự động tổng hợp và gửi bản tin buổi sáng (trước giờ mở cửa) và buổi chiều (sau đóng cửa) đến Telegram của người dùng.

**Nội dung bản tin bao gồm:**
- Tổng quan VN-Index, HNX-Index, UPCOM: điểm số, % thay đổi, khối lượng giao dịch
- Top 5 cổ phiếu tăng mạnh nhất / giảm mạnh nhất trong ngày
- Khối ngoại mua/bán ròng nhiều nhất
- Thanh khoản thị trường so với trung bình 20 phiên
- Các sự kiện quan trọng: họp ĐHCĐ, chia cổ tức, phát hành thêm, niêm yết mới
- Tin tức nóng từ các nguồn: CafeF, VnEconomy, Vietstock, HoSE, HNX

**Thời điểm gửi đề xuất:**
- **8:00 sáng:** Bản tin trước giờ mở cửa — định hướng phiên giao dịch
- **15:30 chiều:** Bản tin kết phiên — tổng kết và nhận định
- **Tuỳ chỉnh:** Người dùng có thể chọn khung giờ nhận tin

---

### 2.2. 🌐 Tin Tức Chứng Khoán Thế Giới Ảnh Hưởng Đến VN

**Mô tả:** Theo dõi và lọc các sự kiện kinh tế, tài chính toàn cầu có tác động tiềm tàng đến thị trường Việt Nam.

**Nguồn theo dõi:**
- Fed (Cục Dự trữ Liên bang Mỹ): quyết định lãi suất, biên bản họp FOMC
- Dow Jones, S&P 500, Nasdaq, Nikkei 225, Hang Seng — diễn biến các phiên trước
- Giá dầu thô (Brent, WTI), giá vàng thế giới, tỷ giá USD/VND
- Chỉ số sợ hãi VIX
- Tin tức địa chính trị ảnh hưởng chuỗi cung ứng (xung đột, thương mại quốc tế)
- Số liệu kinh tế vĩ mô Mỹ: CPI, PPI, Non-Farm Payroll, GDP

**Cách xử lý:** Dùng AI để đánh giá mức độ tác động đến VN-Index (tích cực / tiêu cực / trung lập) và giải thích ngắn gọn lý do.

---

### 2.3. 📊 Phân Tích Xu Hướng 10 Mã Chứng Khoán Cá Nhân Hóa

**Mô tả:** Người dùng tự cấu hình danh sách tối đa 10 mã cổ phiếu quan tâm. Hệ thống phân tích và gửi báo cáo định kỳ hoặc khi có tín hiệu đáng chú ý.

**Nội dung phân tích mỗi mã:**

| Hạng mục | Chi tiết |
|---|---|
| Giá hiện tại | Giá đóng cửa, % thay đổi, so với đỉnh/đáy 52 tuần |
| Xu hướng kỹ thuật | MA20, MA50, MA200 — trên/dưới đường trung bình |
| Chỉ báo động lượng | RSI (14), MACD — tín hiệu mua/bán |
| Khối lượng giao dịch | So sánh với trung bình 20 phiên — phát hiện bất thường |
| Mức hỗ trợ/kháng cự | 3 mức gần nhất tính theo kỹ thuật |
| Nhận định AI | Xu hướng ngắn hạn (3-5 phiên): Tăng / Đi ngang / Giảm |
| Cảnh báo đặc biệt | Đột biến khối lượng, phá vỡ kháng cự, vào/ra vùng quá mua/quá bán |

**Cài đặt cảnh báo linh hoạt:**
- Cảnh báo khi giá vượt ngưỡng người dùng đặt (VD: VCB > 95,000)
- Cảnh báo khi RSI < 30 (quá bán) hoặc RSI > 70 (quá mua)
- Cảnh báo khi khối lượng giao dịch tăng đột biến > 200% trung bình

---

### 2.5. 📝 Quản Lý Blog & Cộng Đồng Phân Tích

**Mô tả:** Nền tảng blog tích hợp ngay trong ứng dụng, cho phép đội ngũ biên tập viên đăng bài chính thức và người dùng chia sẻ phân tích chứng khoán cá nhân với cộng đồng.

---

#### 👨‍💼 Dành Cho Admin / Biên Tập Viên (Official Blog)

**Quản lý bài viết chính thức:**
- Tạo, chỉnh sửa, xoá và xuất bản bài phân tích thị trường
- Trình soạn thảo rich text (Markdown + WYSIWYG) với hỗ trợ nhúng biểu đồ
- Trạng thái bài viết: **Nháp → Chờ duyệt → Đã xuất bản → Lưu trữ**
- Lên lịch xuất bản tự động (VD: đăng bài lúc 7:30 sáng)
- Gắn thẻ mã cổ phiếu liên quan (VD: `#VCB`, `#VHM`, `#FPT`)

**Phân loại & Tổ chức:**
- Danh mục bài viết: Phân tích kỹ thuật / Phân tích cơ bản / Vĩ mô / Tin tức / Hướng dẫn
- Gắn tag tự do và tag mã cổ phiếu
- Ảnh bìa bài viết và ảnh nội dung
- Cài đặt SEO: meta title, meta description, slug tuỳ chỉnh

**Phân phối nội dung:**
- Tự động gửi bài viết mới lên Telegram channel của ứng dụng
- Nút "Chia sẻ Telegram" trực tiếp trong bài
- RSS Feed cho blog chính thức

---

#### 🧑‍💻 Dành Cho Người Dùng (Community Blog)

**Viết & Chia sẻ:**
- Người dùng đã đăng nhập có thể đăng bài phân tích cá nhân
- Trình soạn thảo Markdown đơn giản với preview real-time
- Đính kèm ảnh chụp màn hình biểu đồ
- Gắn tag mã cổ phiếu để bài hiện trong trang theo dõi mã đó

**Kiểm duyệt & Chất lượng:**
- Bài người dùng cần được admin duyệt trước khi công khai (trạng thái **Chờ kiểm duyệt**)
- Hệ thống auto-filter từ ngữ không phù hợp
- Người dùng bị báo cáo nhiều lần sẽ bị hạn chế đăng bài
- Badge "Verified Analyst" cho người dùng có chất lượng bài viết cao

**Tương tác cộng đồng:**
- Like / Bookmark bài viết
- Bình luận và phản hồi bình luận
- Theo dõi tác giả — nhận thông báo khi họ đăng bài mới
- Đếm lượt xem, hiển thị bài viết nổi bật

---

#### 🔍 Tính Năng Chung

**Tìm kiếm & Khám phá:**
- Tìm kiếm full-text theo tiêu đề, nội dung, tag mã cổ phiếu
- Lọc theo: Danh mục / Tác giả / Mã cổ phiếu / Mới nhất / Nổi bật
- Trang riêng cho mỗi mã cổ phiếu tổng hợp tất cả bài viết liên quan

**Tích hợp với tính năng khác:**
- Bài phân tích hiện trong trang chi tiết mã cổ phiếu (mục 2.3)
- Bản tin Telegram buổi sáng có thể đính kèm link bài đọc đáng chú ý
- Người dùng gói Pro/Premium được đăng không giới hạn; Free bị giới hạn 2 bài/tháng

**Schema Database bổ sung:**

| Bảng | Các trường chính |
|---|---|
| `posts` | id, author_id, title, slug, content, status, type (official/community), published_at |
| `post_tags` | post_id, tag (mã CK hoặc chủ đề) |
| `post_likes` | post_id, user_id, created_at |
| `post_comments` | id, post_id, user_id, content, parent_id, created_at |
| `post_bookmarks` | post_id, user_id |
| `author_follows` | follower_id, following_id |

---

### 2.4. 🔐 Đăng Ký / Đăng Nhập Qua Google Auth

**Mô tả:** Người dùng xác thực bằng tài khoản Google — không cần tạo mật khẩu riêng.

**Luồng xác thực:**
1. Người dùng truy cập web app / mở Telegram bot
2. Nhấn "Đăng nhập với Google" → redirect đến Google OAuth 2.0
3. Cấp quyền → Google trả về access token
4. Hệ thống tạo/cập nhật hồ sơ người dùng trong database
5. Liên kết tài khoản Google với Telegram ID của người dùng

**Thông tin lưu trữ:**
- Google ID, email, tên hiển thị, avatar
- Telegram Chat ID (sau khi người dùng kết nối bot)
- Danh sách 10 mã cổ phiếu theo dõi
- Cài đặt thông báo (giờ nhận tin, loại cảnh báo)
- Lịch sử bản tin đã nhận

---

## 3. Kiến Trúc Hệ Thống Đề Xuất

```
┌─────────────────────────────────────────────────────┐
│                   NGƯỜI DÙNG                        │
│         Web App / Telegram Bot                      │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
               ▼                      ▼
┌──────────────────────┐   ┌─────────────────────────┐
│   Google OAuth 2.0   │   │     Telegram Bot API    │
│   (Xác thực)         │   │   (Gửi bản tin / Alert) │
└──────────┬───────────┘   └────────────┬────────────┘
           │                            │
           └────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │       Backend API        │
         │   (Node.js / Python)     │
         │                          │
         │  - Auth Service          │
         │  - User Config Service   │
         │  - Notification Scheduler│
         │  - AI Analysis Engine    │
         │  - Blog & CMS Service    │
         └──────────┬───────────────┘
                    │
        ┌───────────┼───────────────┐
        ▼           ▼               ▼
┌──────────────┐ ┌────────┐ ┌──────────────────┐
│  Database    │ │ Cache  │ │  Data Sources    │
│  PostgreSQL  │ │ Redis  │ │  - HoSE/HNX API  │
│              │ │        │ │  - CafeF RSS     │
│              │ │        │ │  - Alpha Vantage │
│              │ │        │ │  - Yahoo Finance │
└──────────────┘ └────────┘ └──────────────────┘
```

---

## 4. Tech Stack Đề Xuất

### Backend
- **Ngôn ngữ:** Python (FastAPI) hoặc Node.js (Express)
- **Scheduler:** APScheduler (Python) hoặc node-cron
- **AI/NLP:** OpenAI API hoặc Gemini API để tóm tắt tin tức & phân tích xu hướng
- **Message Queue:** Redis + Celery (xử lý gửi thông báo hàng loạt)

### Frontend (Web Dashboard)
- **Framework:** Next.js (React) + TailwindCSS
- **Biểu đồ:** TradingView Lightweight Charts hoặc Recharts
- **Auth:** NextAuth.js tích hợp Google OAuth
- **Blog Editor:** Tiptap hoặc Milkdown (rich text / Markdown editor)
- **Blog Rendering:** MDX với syntax highlight cho code

### Database
- **Chính:** PostgreSQL — lưu user, watchlist, cài đặt, bài blog, bình luận
- **Cache:** Redis — lưu dữ liệu giá real-time, tránh gọi API quá nhiều
- **Full-text Search:** PostgreSQL FTS hoặc Meilisearch — tìm kiếm bài blog nhanh

### Dữ Liệu Chứng Khoán
- **Dữ liệu VN:** API của FireAnt, VNDirect, hoặc scraping CafeF
- **Dữ liệu quốc tế:** Yahoo Finance API, Alpha Vantage (miễn phí)
- **Tin tức:** RSS Feed từ CafeF, VnEconomy, Reuters, Bloomberg

### Telegram
- **Thư viện:** python-telegram-bot hoặc Grammy (Node.js)
- **Bot commands:** `/start`, `/watchlist`, `/settings`, `/report`

---

## 5. Mô Hình Kinh Doanh (Monetization)

| Gói | Tính năng | Giá đề xuất |
|---|---|---|
| **Free** | 3 mã theo dõi, 1 bản tin/ngày, tin tức cơ bản, đọc blog, đăng 2 bài/tháng | Miễn phí |
| **Pro** | 10 mã, 2 bản tin/ngày, cảnh báo real-time, phân tích AI, đăng blog không giới hạn, badge Analyst | 99,000 VND/tháng |
| **Premium** | Không giới hạn mã, phân tích chuyên sâu, tư vấn danh mục, badge Verified Analyst, ưu tiên duyệt bài | 299,000 VND/tháng |

---

## 6. Lộ Trình Phát Triển (Roadmap)

### Giai đoạn 1 — MVP (Tháng 1-2)
- [ ] Xây dựng Telegram Bot cơ bản
- [ ] Tích hợp Google OAuth
- [ ] Thu thập dữ liệu VN-Index, HNX-Index
- [ ] Gửi bản tin tự động hằng ngày

### Giai đoạn 2 — Core Features (Tháng 3-4)
- [ ] Cấu hình watchlist 10 mã cổ phiếu
- [ ] Phân tích kỹ thuật cơ bản (MA, RSI, MACD)
- [ ] Cảnh báo giá theo ngưỡng
- [ ] Web dashboard cơ bản

### Giai đoạn 3 — AI & Nâng Cao (Tháng 5-6)
- [ ] Tích hợp AI phân tích tin tức
- [ ] Phân tích xu hướng bằng AI
- [ ] Theo dõi tin tức quốc tế ảnh hưởng VN
- [ ] Mô hình Freemium & thanh toán

### Giai đoạn 4 — Blog & Cộng Đồng (Tháng 7-8)
- [ ] Blog chính thức: CMS cho admin/biên tập viên
- [ ] Blog cộng đồng: cho phép user đăng bài phân tích
- [ ] Hệ thống kiểm duyệt bài viết
- [ ] Tính năng like, bình luận, theo dõi tác giả
- [ ] Full-text search bài viết theo mã cổ phiếu
- [ ] Tích hợp blog vào bản tin Telegram

---

## 7. Rủi Ro & Lưu Ý

**Pháp lý:**
- Không cung cấp lời khuyên đầu tư trực tiếp — chỉ cung cấp thông tin và phân tích kỹ thuật
- Cần disclaimer rõ ràng: "Đây không phải khuyến nghị đầu tư"

**Dữ liệu:**
- Cần kiểm tra điều khoản sử dụng của các nguồn dữ liệu (HoSE, CafeF...)
- Tránh scraping quá mức — ưu tiên API chính thức

**Bảo mật:**
- Không lưu thông tin nhạy cảm tài chính của người dùng
- Mã hóa Telegram Chat ID và dữ liệu cá nhân
- Tuân thủ GDPR/PDPA

---

## 8. Điểm Khác Biệt Cạnh Tranh

- **Cá nhân hóa cao:** Mỗi người dùng nhận bản tin riêng theo watchlist của họ
- **Không cần mở app:** Nhận thông tin trực tiếp qua Telegram — tiện lợi tối đa
- **AI-powered:** Phân tích xu hướng và tóm tắt tin tức tự động, không chỉ là số liệu thô
- **Thị trường ngách:** Tập trung vào nhà đầu tư cá nhân Việt Nam — chưa có nhiều sản phẩm tương tự chất lượng cao
- **Cộng đồng tri thức:** Blog tích hợp cho phép cả chuyên gia lẫn nhà đầu tư cá nhân chia sẻ phân tích — tạo network effect và giữ chân người dùng lâu dài

---

*Tài liệu này được soạn thảo bởi AI Financial Consultant — StockPulse VN Concept v1.1 (cập nhật: thêm tính năng Blog & Cộng đồng)*