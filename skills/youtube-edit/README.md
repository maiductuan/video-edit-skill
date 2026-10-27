# YouTube Edit (`/youtube-edit`)

Skill chuyên dựng **video YouTube ngang 16:9 (1080p60 / 4K)** dành cho **Vlog trải nghiệm, Review Ẩm thực / Du lịch / Khám phá và Talking-head** trên Antigravity.

---

## Tính năng chính

1. **Phân loại & Nhận diện thông minh (`ingest.py`)**
   - Tự động quét các clip rời từ điện thoại/máy ảnh, phân loại **A-Roll** (cảnh có người nói trực tiếp) và **B-Roll** (cảnh quay đồ ăn, không gian, phố phường).
   - Nhận diện giọng nói **Tiếng Việt & Tiếng Anh** (`faster-whisper`) tới từng câu/từ kèm bản đồ khoảng lặng (`silencedetect`).
   - Xuất bảng ảnh thu nhỏ 16:9 (`work/sheets.jpg`) giúp kiểm tra góc máy và chất lượng cảnh quay.

2. **Dựng Timeline 16:9 chuẩn Vlog & Talking-Head (`assemble.py`)**
   - **Cắt khoảng nghỉ & Lọc câu nói vấp:** Tự động giữ lại take tốt nhất và loại bỏ khoảng lặng thừa.
   - **Lồng B-Roll trên nền giọng nói A-Roll (J/L Cut):** Giữ nguyên giọng bạn đang thuyết minh/review món ăn trong khi hình ảnh chuyển sang cảnh cận cảnh món ăn hoặc không gian quán (`aroll_with_broll`).
   - **Tự động Punch-in 4K:** Phóng nhẹ `1.25x–1.45x` khi ghép nối hai đoạn nói liên tiếp cùng một góc máy.

3. **Bộ Đồ họa YouTube 16:9 Chuyên Nghiệp (`build_graphics.py`)**
   Hỗ trợ đầy đủ **tiếng Việt có dấu chuẩn Unicode** với hiệu ứng chuyển động mượt và âm thanh SFX đi kèm:
   - **Intro Title Card (`intro`):** Đại tự tiêu đề mở đầu vlog kèm badge tập/chủ đề và dòng mô tả phụ.
   - **Chapter Divider (`chapter`):** Thẻ chia chương/phân đoạn có đánh số (`CHƯƠNG 01`, `CHƯƠNG 02`...).
   - **Review / Location Lower-Third (`lower_third`):** Thẻ thông tin góc dưới bên trái hiển thị **Tên món ăn / Địa điểm**, **Địa chỉ (📍)**, **Giá tiền (💰)** và **Điểm đánh giá (⭐ 9.2/10)**.
   - **Callout / Tip Badge (`callout`):** Hộp ghi chú/mẹo nhỏ bật lên ở góc trên bên phải.
   - **YouTube Subscribe CTA (`subscribe`):** Thẻ kêu gọi **ĐĂNG KÝ (SUBSCRIBE) + Chuông thông báo** kèm tên kênh.
   - **Phụ đề Tiếng Việt (`subtitles`):** Phụ đề `.ass` bo viền hoặc nền bán trong suốt dễ đọc ở cạnh dưới khung hình 16:9.

4. **Chỉnh màu, Auto-Ducking BGM & Xuất 1080p60 tốc độ cao (`render.py`)**
   - 3 bộ màu (Looks): `vibrant_vlog` (ấm áp, tôn màu ẩm thực/du lịch), `cinema_travel` (điện ảnh), `clean_studio` (trong trẻo cho talking-head).
   - Tự động trộn nhạc nền (BGM) với **Auto-Ducking** (tự giảm âm lượng nhạc khi có giọng nói và nâng nhạc lên ở cảnh B-roll) + hiệu ứng âm thanh (`whoosh`, `pop`, `sparkle`, `click`).
   - Tự động xuất bảng kiểm tra chất lượng (`work/qa_sheet.jpg`) chụp lại mọi điểm cắt và đồ họa.

5. **Trích xuất YouTube Shorts 9:16 (`extract_shorts.py`)**
   - Cắt nhanh một đoạn highlight từ video ngang 16:9 sang khung dọc 9:16 (1080×1920) có nền mờ (blurred backdrop) và tiêu đề phía trên.

---

## Cách gọi Skill

Gõ trong khung chat:
- `/youtube-edit dựng các clip trong thư mục này thành vlog YouTube`
- `/youtube-edit thêm intro, chia chapter và lower-third giá tiền/địa điểm cho video`
