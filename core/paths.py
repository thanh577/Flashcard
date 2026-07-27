
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

    - Khi chạy từ .exe đã đóng gói: `%APPDATA%\\FlashcardApp` trên Windows
      (hoặc `~/.flashcardapp` trên hệ điều hành khác, phòng khi build/test
      không phải Windows) — thư mục này KHÔNG bị xoá khi app thoát, khác với
      thư mục tạm `sys._MEIPASS` của PyInstaller.
    - Khi chạy từ mã nguồn (đang phát triển): vẫn dùng thư mục `data/` ngay
      trong dự án như trước giờ — không đổi trải nghiệm lúc code/debug.
    """
    if is_frozen():
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, APP_NAME)
    else:
        d = os.path.join(_project_root(), "data")
    os.makedirs(d, exist_ok=True)
    return d
