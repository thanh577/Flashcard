
BBI V4 INTERNAL TOOL — Flashcard học Anh / Trung / Linux
==========================================================

🚨 BẮT BUỘC ĐỌC TRƯỚC: PHẢI BUILD TRÊN MÁY WINDOWS THẬT 🚨
----------------------------------------------------------
PyInstaller KHÔNG hỗ trợ build chéo hệ điều hành — nó luôn tạo ra file thực
thi theo ĐÚNG hệ điều hành đang chạy lệnh:

    Chạy lệnh trên Linux  → tạo file định dạng ELF (Linux) — KHÔNG chạy được
                             trên Windows, dù đổi tên thành .exe cũng vô ích
                             (Windows đọc header file để nhận diện định dạng,
                             không dựa vào đuôi file)
    Chạy lệnh trên Windows → tạo file định dạng PE (Windows) — mới là file
                             .exe thật, chạy được trên Windows

⚠️ Nếu bạn build thử trên Linux/WSL/máy ảo Linux để kiểm tra code chạy đúng
không, đó CHỈ có giá trị kiểm tra logic — không bao giờ dùng file build ra
từ đó để phát hành cho Windows. Phải chạy đúng lệnh `pyinstaller
FlashcardApp.spec` NGAY TRÊN một máy Windows thật thì mới ra được file .exe
dùng được.

CHỈ CÓ MÁY LINUX, KHÔNG CÓ MÁY WINDOWS NÀO CẢ? → xem mục 7 bên dưới, dùng
GitHub Actions để mượn 1 máy Windows thật miễn phí, không cần cài Windows.


1) CÀI ĐẶT MÔI TRƯỜNG BUILD (chỉ cần làm 1 lần, TRÊN MÁY WINDOWS)
----------------------------------------------------------
pip install pyqt6 pyinstaller


2) BUILD RA FILE .EXE (kèm đầy đủ dữ liệu)
----------------------------------------------------------
Đứng ở THƯ MỤC GỐC của dự án (nơi có file app.py), chạy đúng lệnh sau:

    pyinstaller FlashcardApp.spec

⚠️ KHÔNG dùng "pyinstaller --onefile app.py" trực tiếp — lệnh đó bỏ qua
toàn bộ phần "datas" (3 file JSON hạt giống + icon) đã khai báo sẵn trong
FlashcardApp.spec. Phải build đúng từ file .spec này thì dữ liệu mới được
đóng gói kèm vào exe.

Build xong, file duy nhất cần dùng là:

    dist/FlashcardApp.exe

Copy đúng 1 file này sang máy Windows khác là chạy được ngay — KHÔNG cần
mang theo thư mục data/, core/, ui/ hay bất kỳ file .py nào khác.


3) VÌ SAO EXE NÀY "CÓ FULL DATA" — CƠ CHẾ HOẠT ĐỘNG
----------------------------------------------------------
Exe mang theo 2 loại dữ liệu, xử lý khác nhau (xem core/paths.py):

  a) Dữ liệu HẠT GIỐNG (chỉ đọc) — 3 file JSON (english/chinese/linux) +
     app_icon.png — đóng gói CỨNG vào bên trong exe. Chỉ dùng để tạo DB
     mới toanh trong lần chạy đầu tiên trên 1 máy.

  b) Dữ liệu SỐNG (đọc/ghi) — flashcard.db (tiến độ học) + config.json
     (cài đặt) — KHÔNG đóng gói vào exe. Lần đầu chạy trên 1 máy, app tự
     tạo 2 file này tại:

         %APPDATA%\FlashcardApp\

     Thư mục này KHÔNG bị xoá khi đóng app (khác hẳn thư mục tạm mà
     PyInstaller --onefile tự xoá mỗi lần thoát) — nhờ vậy tiến độ học
     (interval, streak, yêu thích...) được giữ nguyên qua các lần mở lại.


4) KIỂM TRA SAU KHI BUILD (nên làm trước khi phát cho đồng nghiệp)
----------------------------------------------------------
- Copy dist/FlashcardApp.exe sang một máy Windows KHÁC (USB, Zalo, email...)
  — chọn máy CHƯA từng cài/chạy app này bao giờ để test đúng tình huống
  "máy mới".
- Chạy file .exe — app phải mở lên NGAY với đầy đủ thẻ, không báo lỗi
  thiếu file, không màn hình trắng.
- Vào Cài đặt, bật cả 3 nguồn (Anh/Trung/Linux), kiểm tra tổng số thẻ đúng
  bằng dữ liệu gốc.
- Kiểm tra thư mục %APPDATA%\FlashcardApp\ đã tự được tạo, có 2 file
  flashcard.db và config.json.
- Đóng app, mở lại — tiến độ vừa học không bị mất, không bị tạo lại từ đầu.


5) MUỐN "RESET" VỀ TRẠNG THÁI BAN ĐẦU (xoá hết tiến độ đã học)
----------------------------------------------------------
Xoá thư mục:

    %APPDATA%\FlashcardApp\

rồi mở lại app — app tự tạo lại từ đầu, seed đúng dữ liệu gốc đóng gói
trong exe, y như máy mới.


6) LƯU Ý KHI BUILD THỬ TRÊN LINUX/MAC (không phải bản phát hành)
----------------------------------------------------------
- Icon (app_icon.ico) chỉ được nhúng vào file thực thi khi build TRÊN
  Windows hoặc macOS — PyInstaller bỏ qua icon khi build trên Linux (đây
  chỉ là giới hạn của máy đang build, không phải lỗi trong code).
- Muốn có bản chính thức để phát cho đồng nghiệp, nên build TRÊN MỘT MÁY
  WINDOWS THẬT — không build trên Linux/WSL rồi mang exe kết quả sang
  Windows, vì PyInstaller đóng gói executable theo đúng hệ điều hành đang
  chạy lúc build, exe build trên Linux sẽ KHÔNG chạy được trên Windows.


7) CHỈ CÓ MÁY LINUX? DÙNG GITHUB ACTIONS ĐỂ MƯỢN MÁY WINDOWS THẬT (MIỄN PHÍ)
----------------------------------------------------------
Dự án đã có sẵn file `.github/workflows/build-windows.yml` — 1 "công thức"
để GitHub tự động cấp 1 máy Windows THẬT (không phải giả lập/Wine), chạy
đúng lệnh build, rồi cho bạn tải file .exe về. Miễn phí với tài khoản
GitHub thường (kể cả repo riêng tư).

CÁCH DÙNG (làm 1 lần):

  a) Tạo tài khoản GitHub (nếu chưa có) tại github.com — miễn phí.

  b) Tạo 1 repository mới (public hoặc private đều được), rồi đưa TOÀN BỘ
     thư mục dự án này lên đó. 2 cách:

     - Có sẵn git: mở terminal tại thư mục dự án, chạy:
         git init
         git add .
         git commit -m "Flashcard app"
         git branch -M main
         git remote add origin <đường-dẫn-repo-bạn-vừa-tạo>
         git push -u origin main

     - Không quen dùng git: vào trang repo trên GitHub, bấm nút
       "Add file" → "Upload files", kéo thả toàn bộ file/thư mục dự án
       (kể cả thư mục ẩn `.github/`) vào rồi bấm "Commit changes".

  c) Vào tab "Actions" trên trang repo — workflow "Build Windows EXE + Linux
     AppImage" sẽ tự chạy ngay sau khi push/upload xong (mất khoảng 3-5
     phút, build cả bản Windows lẫn Linux cùng lúc). Nếu không tự chạy, bấm
     vào workflow đó → nút "Run workflow" để chạy thủ công.

  d) Chờ chạy xong (dấu tích xanh ✔), bấm vào lần chạy đó, kéo xuống mục
     "Artifacts" — sẽ thấy CẢ 2 file:
       - "FlashcardApp-windows.zip" → giải nén ra FlashcardApp.exe (Windows)
       - "FlashcardApp-linux.zip"   → giải nén ra FlashcardApp-x86_64.AppImage (Ubuntu/Linux)

Mỗi lần bạn sửa code và push/upload lại, workflow này sẽ tự chạy lại và tạo
bản mới cho cả 2 hệ điều hành — không cần lặp lại các bước cài đặt.


8) BUILD RA FILE .APPIMAGE ĐỂ CHẠY TRÊN UBUNTU/LINUX
----------------------------------------------------------
Khác với Windows, AppImage build được ngay TRÊN MÁY LINUX BẠN ĐANG CÓ —
không cần mượn máy khác hay dùng GitHub Actions (dù mục 7 ở trên cũng tự
build AppImage kèm theo nếu bạn dùng GitHub).

CÀI ĐẶT (nếu chưa có):
    pip install pyqt6 pyinstaller

BUILD (1 lệnh duy nhất, đã tự động hoá toàn bộ các bước):
    bash build_appimage.sh

Script này tự làm hết: build bằng PyInstaller → dựng cấu trúc AppDir → tải
appimagetool (nếu máy chưa có, khoảng 15MB, chỉ tải 1 lần) → đóng gói thành
file .AppImage. Kết quả nằm ở:

    FlashcardApp-x86_64.AppImage

CHẠY THỬ / MANG SANG MÁY LINUX KHÁC:
    chmod +x FlashcardApp-x86_64.AppImage
    ./FlashcardApp-x86_64.AppImage

Không cần cài Python/PyQt6 gì thêm trên máy đích — mọi thứ đã đóng gói sẵn
trong 1 file, y hệt tinh thần file .exe của Windows. Cũng seed đủ dữ liệu
gốc (456 thẻ) ngay lần chạy đầu tiên, lưu tiến độ vào:

    ~/.local/share/FlashcardApp/   (tương đương %APPDATA% bên Windows)

LƯU Ý: AppImage build trên máy Linux nào thì nên chạy được trên hầu hết bản
Ubuntu/Linux khác cùng kiến trúc x86_64 — nhưng nếu máy đích dùng bản Linux
rất cũ (thư viện hệ thống cũ hơn máy build), đôi khi vẫn có thể gặp lỗi
thiếu thư viện. Muốn chắc chắn nhất, nên build trên bản Ubuntu LTS phổ biến
(22.04 hoặc 24.04) — hoặc dùng bản build tự động từ GitHub Actions ở mục 7,
vì máy ảo Ubuntu của GitHub cũng là bản phổ biến, tương thích rộng.

