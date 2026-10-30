# YouTube Edit (`/youtube-edit`)

Skill chuyên dựng **video YouTube ngang 16:9 (1080p60 / 4K)** dành cho **Vlog trải nghiệm, Review Ẩm thực / Du lịch / Khám phá và Talking-head** — tự động sinh **hình ảnh minh họa AI (AI B-roll & Visual Cards)** và **Motion Graphics chuyển động đa khung hình** để video luôn sinh động, không bao giờ bị đơ hay khô.

---

## Tính năng chính

1. **Phân loại & Nhận diện thông minh (`ingest.py`)**
   - Tự động quét các clip rời (và ảnh tư liệu), phân loại **A-Roll** (cảnh người nói), **B-Roll** (cảnh quay đồ ăn, không gian, phố phường) và **IMAGE-BROLL** (ảnh chụp / ảnh AI minh họa).
   - Nhận diện giọng nói **Tiếng Việt & Tiếng Anh** (`faster-whisper`) tới từng câu/từ kèm bản đồ khoảng lặng (`silencedetect`).
   - Xuất bảng ảnh thu nhỏ 16:9 (`work/sheets.jpg`) giúp kiểm tra bố cục khung hình trước khi đặt đồ họa.

2. **Tạo B-Roll Chân Thực Chuẩn Điện Ảnh TVC & Optical Plate Matching (`assemble.py` + `image-generator`)**
   - **Không để Talking-Head đứng yên quá 6 giây — Không nhìn "giả AI":** Khi thiếu B-roll thực tế, AI chủ động tạo ảnh chụp phong cách **35mm Live-Action Commercial (ARRI Alexa / Sony FX3, ống kính 50mm f/2.0, ánh sáng tự nhiên)** tập trung vào cận cảnh đồ vật, món ăn, không gian kiến trúc (tuyệt đối tránh vẽ mặt/bàn tay người AI hoặc phong cách neon/hoạt hình).
   - **Optical Sensor Match & Gimbal Inertia:** Tự động khử độ bão hòa/tương phản "nhựa" đặc trưng của ảnh AI, thêm độ tối góc ống kính tự nhiên (`vignette`), hạt cảm biến luma siêu mịn (`35mm sensor micro-dither`) và chuyển động trượt dolly mượt theo quán tính hình sin (`4.5%–6.2%`).

3. **11 Mẫu Đồ Họa Broadcast Chuẩn TVC / Netflix Documentary (`build_graphics.py`)**
   Khử sạch kiểu "hộp SaaS tối màu + nút vàng lòe loẹt". Toàn bộ đồ họa được vẽ **khử răng cưa 2x Supersampled Lanczos**, nền kính khói mờ tinh tế (`1px` viền specular hairline), chữ micro-kicker giãn chữ rộng (`+3.4px` tracking) và hiệu ứng chữ trồi lên từ mặt nạ ẩn (`masked baseline reveal` `quintic ease-out`):
   - `intro`: Đại tự điện ảnh không khung hộp (frameless optical scrim) kèm đường kẻ mảnh vàng đồng bung ngang từ tâm.
   - `lower_third` & `chapter`: Dải kính khói tối giản phong cách Michelin Guide / Netflix với vạch laser dọc mọc từ dưới lên và điểm số tối giản (`9.4` + `/10`).
   - `visual_card`: Khung hình PiP viền mỏng `14px` tự động cân chỉnh chất màu phim cho ảnh và trượt gimbal nhẹ bên trong khung (tự động lọc bỏ các nhãn tự tố cáo như `"MINH HỌA AI"`).
   - `stat_card`: Bảng thông số phong cách Apple Keynote với số chạy mượt và đường kẻ thanh mảnh `2.5px` kèm chấm sáng dẫn hướng.
   - `checklist`, `comparison`, `kinetic_quote`, `callout`, `subscribe`, `custom_motion` + Phụ đề điện ảnh `.ass`.

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
