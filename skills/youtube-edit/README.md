# YouTube Edit (`/youtube-edit`)

Skill chuyên dựng **video YouTube ngang 16:9 (1080p60 / 4K)** dành cho **Vlog trải nghiệm, Review Ẩm thực / Du lịch / Khám phá và Talking-head** — tự động sinh **hình ảnh minh họa AI (AI B-roll & Visual Cards)** và **Motion Graphics chuyển động đa khung hình** để video luôn sinh động, không bao giờ bị đơ hay khô.

---

## Tính năng chính

1. **Phân loại & Nhận diện thông minh (`ingest.py`)**
   - Tự động quét các clip rời (và ảnh tư liệu), phân loại **A-Roll** (cảnh người nói), **B-Roll** (cảnh quay đồ ăn, không gian, phố phường) và **IMAGE-BROLL** (ảnh chụp / ảnh AI minh họa).
   - Nhận diện giọng nói **Tiếng Việt & Tiếng Anh** (`faster-whisper`) tới từng câu/từ kèm bản đồ khoảng lặng (`silencedetect`).
   - Xuất bảng ảnh thu nhỏ 16:9 (`work/sheets.jpg`) giúp kiểm tra bố cục khung hình trước khi đặt đồ họa.

2. **Chủ động Tạo Hình Ảnh Minh Họa AI & Chuyển Động Máy Quay (`assemble.py` + `image-generator`)**
   - **Không để Talking-Head đứng yên quá 6 giây:** Khi đoạn nói thiếu B-roll thực tế, AI chủ động tạo ảnh minh họa editorial / ảnh B-roll điện ảnh không chữ vào `assets/ai_visuals/` bằng `image-generator`.
   - **4K-Supersampled 60fps Ken Burns:** Mọi ảnh AI / ảnh tĩnh đưa vào `edl.json` (`type: "broll"` hoặc `broll_inserts`) đều được phóng mẫu 4K (`3840×2160`) và tạo chuyển động máy quay mượt 60fps (`push_in`, `pull_out`, `pan_right`, `pan_left`, `drift_up`) không rung giật pixel.
   - **Dynamic Video Motion & J/L Cut:** Hỗ trợ lồng B-roll trên nền giọng nói liên tục (`aroll_with_broll`), tự động Punch-in 4K và đẩy máy mượt (`motion: "push_in"`) trên cả clip video thật.

3. **11 Mẫu Đồ Họa & Motion Graphics RGBA Chuyển Động Thật (`build_graphics.py`)**
   Hỗ trợ đầy đủ **tiếng Việt có dấu chuẩn Unicode (`Be Vietnam Pro`)** với cả thẻ tiêu chuẩn và **thẻ Motion đa khung hình (`.mov` RGBA 30fps)**:
   - **Thẻ Motion & Hình Ảnh Minh Họa AI (Mới):**
     - `visual_card`: Khung ảnh PiP bên cạnh người nói hiển thị ảnh minh họa AI kèm **hiệu ứng zoom Ken Burns sống động ngay bên trong khung bo góc** + thanh tiến trình accent.
     - `stat_card`: Thẻ số liệu **chạy số đếm tăng dần từ 0** (`0% -> 85%`, `0đ -> 40.000đ`, `0/10 -> 9.2/10`) kết hợp thanh progress bar lấp đầy mượt mà.
     - `checklist` (`steps_card`): Danh sách 2–4 bước / ý chính **bật ra tuần tự từng dòng theo nhịp nói** thay vì hiện cả khối chữ tĩnh.
     - `comparison`: Bảng so sánh đôi **Trước / Sau** hoặc **Điểm trừ / Điểm cộng** xuất hiện 2 nhịp nối tiếp.
     - `kinetic_quote`: Banner trích dẫn / luận điểm cốt lõi với thanh nhấn quét ngang mượt mà.
     - `custom_motion`: Nhúng trực tiếp file animation `.webm` / `.mov` nền trong suốt.
   - **Bộ Thẻ YouTube Truyền Thống:** `intro` (Đại tự mở đầu), `chapter` (Chia chương), `lower_third` (Tên món / Địa chỉ / Giá tiền / Điểm đánh giá), `callout` (Ghi chú góc trên), `subscribe` (Kêu gọi Đăng ký kênh) + **Phụ đề Tiếng Việt `.ass`**.

4. **6 Bộ Màu Điện Ảnh, Auto-Ducking BGM & Chuẩn Âm Thanh `-14 LUFS` (`render.py`)**
   - 6 bộ màu: `vibrant_vlog`, `warm_food`, `cinema_travel`, `clean_studio`, `film_kodak`, `minimal_editorial`.
   - Tự động trộn nhạc nền (BGM) với **Auto-Ducking** + hiệu ứng âm thanh tinh tế (`whoosh-short`, `pop`, `sparkle`, `click`) và chuẩn hóa âm lượng **EBU R128 `-14 LUFS`**.
   - Xuất bảng kiểm tra chất lượng (`work/qa_sheet.jpg`) chụp đúng thời điểm đạt đỉnh chuyển động của mọi thẻ đồ họa.

5. **Trích xuất YouTube Shorts 9:16 (`extract_shorts.py`)**
   - Cắt nhanh đoạn highlight từ video ngang 16:9 sang khung dọc 9:16 (1080×1920) có nền mờ và banner tiêu đề.

---

## Cách gọi Skill

Gõ trong khung chat:
- `/youtube-edit dựng các clip trong thư mục này thành vlog YouTube, tự tạo thêm ảnh minh họa và motion card cho đỡ khô`
- `/youtube-edit thêm intro, chia chapter, thẻ đếm số liệu và lower-third giá tiền/địa điểm cho video`
