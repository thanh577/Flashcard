
import os
import sys

APP_NAME = "FlashcardApp"


def is_frozen():
    """True nếu đang chạy từ file .exe đã đóng gói bằng PyInstaller."""
    return getattr(sys, "frozen", False)


def _project_root():
    # core/ nằm ngay dưới thư mục gốc dự án
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    """Đường dẫn tới tài nguyên CHỈ ĐỌC đóng gói cùng exe (icon, JSON hạt giống
    ban đầu). Khi chạy từ .exe (PyInstaller --onefile), tài nguyên được giải
    nén vào thư mục tạm `sys._MEIPASS` lúc khởi động; khi chạy từ mã nguồn,
    tài nguyên nằm ngay trong thư mục dự án.

    KHÔNG dùng hàm này cho file cần GHI (DB, config) — thư mục _MEIPASS bị xoá
    mỗi khi app thoát, ghi vào đó sẽ mất hết ngay khi đóng app.
    """
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = _project_root()
    return os.path.join(base, *parts)


def user_data_dir():
    """Thư mục GHI ĐƯỢC, tồn tại lâu dài giữa các lần chạy — nơi lưu DB tiến độ
    thật (flashcard.db) và config.json.

    - Windows (đã đóng gói .exe): `%APPDATA%\\FlashcardApp`
    - Linux/macOS (đã đóng gói .AppImage/binary): `~/.local/share/FlashcardApp`
      theo đúng chuẩn XDG Base Directory (tôn trọng biến môi trường
      XDG_DATA_HOME nếu có đặt riêng). TRƯỚC ĐÂY có bug thật: rơi về thẳng
      `~/FlashcardApp` (đổ thẳng vào thư mục home, không theo chuẩn Linux
      nào cả) — gây ra thư mục lạ ngay giữa $HOME, đã sửa.
    - Khi chạy từ mã nguồn (đang phát triển): vẫn dùng thư mục `data/` ngay
      trong dự án như trước giờ — không đổi trải nghiệm lúc code/debug.
    """
    if is_frozen():
        if sys.platform == "win32":
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
            d = os.path.join(base, APP_NAME)
        else:
            xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.join(
                os.path.expanduser("~"), ".local", "share"
            )
            d = os.path.join(xdg_data, APP_NAME)
    else:
        d = os.path.join(_project_root(), "data")
    os.makedirs(d, exist_ok=True)
    return d
