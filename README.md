# 🎵 MP3 320kbps Downloader (YouTube & TikTok)

Công cụ dòng lệnh (CLI) tải âm thanh chất lượng cao chuẩn **320kbps MP3** từ **YouTube** (Video, Shorts, Music, Playlist), **TikTok** (Video, Photo slide, Âm thanh gốc), Facebook Reels, Instagram và nhiều nền tảng khác.

---

## 🌟 Tính Năng Nổi Bật

- 🎧 **Âm thanh chuẩn 320kbps**: Trích xuất và encode âm thanh MP3 với bitrate cao nhất (320kbps CBR) qua FFmpeg.
- 🖼️ **Tự động nhúng ảnh bìa (Album Art)**: Tải thumbnail chất lượng cao và nhúng trực tiếp vào file MP3, hiển thị ảnh bìa đẹp mắt trên điện thoại, máy tính, ô tô.
- 🏷️ **Ghi nhãn ID3 Metadata**: Tự động lưu tiêu đề, ca sĩ/kênh sáng tạo, thời lượng vào thẻ thông tin của bài hát.
- 🚀 **Hỗ trợ đa nền tảng**:
  - **YouTube**: Video thường, YouTube Shorts, YouTube Music, Playlist danh sách bài hát.
  - **TikTok**: Link video tiêu chuẩn, link rút gọn điện thoại (`vt.tiktok.com`), âm thanh gốc TikTok.
  - **Khác**: Facebook Videos/Reels, Instagram Reels, SoundCloud, Twitter/X.
- 🖥️ **Giao diện dòng lệnh trực quan (Rich UI)**: Bảng thông tin, thanh tiến trình % tải về, tốc độ tải (MB/s), thời gian còn lại (ETA).
- 📑 **Hỗ trợ tải hàng loạt**: Nhập nhiều link cùng lúc hoặc đọc từ file `links.txt`.
- ⚡ **Tự tích hợp FFmpeg**: Không cần cài đặt hay cấu hình biến môi trường thủ công.

---

## 🚀 Cách Sử Dụng

### Cách 1: Chạy bằng giao diện tương tác (Khuyên dùng)
Bạn chỉ cần mở thư mục `media-mp3-downloader` và:
- **Click đúp vào file `run.bat`** (trên Windows).
- Hoặc mở Terminal / PowerShell tại thư mục này và gõ:
  ```powershell
  python main.py
  ```

Hệ thống sẽ hiển thị Menu lựa chọn:
```text
[1] 🚀 Tải 1 link (Dán link YouTube, Shorts, TikTok)
[2] 📑 Tải danh sách nhiều link (Nhập liên tục nhiều dòng)
[3] 📂 Tải danh sách từ file links.txt
[4] 📁 Mở thư mục chứa file đã tải (downloads)
[5] ⚙️  Cài đặt chất lượng & ảnh bìa
[6] ℹ️  Xem các nền tảng hỗ trợ
[0] ❌ Thoát chương trình
```

---

### Cách 2: Tải nhanh qua lệnh dòng lệnh (CLI Arguments)

1. **Tải 1 link bất kỳ:**
   ```powershell
   python main.py "https://www.youtube.com/watch?v=..."
   ```
   hoặc:
   ```powershell
   python main.py "https://vt.tiktok.com/..."
   ```

2. **Tải nhiều link cùng lúc:**
   ```powershell
   python main.py "link_1" "link_2" "link_3"
   ```

3. **Tải danh sách từ file văn bản:**
   Dán các đường link vào file `links.txt` (mỗi dòng 1 link), sau đó chạy:
   ```powershell
   python main.py -f links.txt
   ```

4. **Tùy chỉnh thư mục lưu và tự động mở thư mục khi tải xong:**
   ```powershell
   python main.py "URL" -o "D:/Music" --open
   ```

5. **Tùy chỉnh bitrate khác (nếu muốn file nhẹ hơn):**
   ```powershell
   python main.py "URL" -q 192    # các mức: 128, 192, 256, 320
   ```

---

## 📁 Thư Mục Lưu Trữ
Mặc định tất cả các file MP3 sau khi tải và chuyển đổi thành công sẽ tự động chuyển vào thư mục của trình phát nhạc:
```text
d:/code/html/music-player/NHAC
```

---

## 🛠️ Cài Đặt Thư Viện (Nếu chuyển sang máy tính khác)
Chỉ cần chạy lệnh:
```powershell
pip install -r requirements.txt
```
