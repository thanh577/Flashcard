
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from core.theme import QSS
from core.paths import resource_path, user_data_dir

# QUAN TRỌNG: exe đóng gói với console=False (--noconsole) không có console để
# hiển thị log — nếu chỉ dùng logging.basicConfig() mặc định (ghi ra stderr),
# TOÀN BỘ log sẽ biến mất trên bản exe thật, dù code có gọi logger.error() đầy
# đủ ở khắp nơi. Phải ghi ra FILE trong thư mục dữ liệu bền vững thì mới có gì
# để xem lại khi debug — đặc biệt quan trọng với tool nội bộ, vì người dùng
# không tự xem được console khi có lỗi.
_log_path = os.path.join(user_data_dir(), "app.log")
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(_log_path, maxBytes=1_000_000, backupCount=2, encoding="utf-8"),
    ],
)

_logger = logging.getLogger("crash")


def _log_uncaught_exception(exc_type, exc_value, exc_tb):
    """Bắt MỌI lỗi chưa được xử lý ở đâu đó trong app — nếu không có hook này,
    app sẽ tắt/đơ mà không để lại dấu vết gì để debug (đặc biệt nguy hiểm với
    tool nội bộ: người dùng thấy app "biến mất", không biết báo lỗi gì)."""
    _logger.error("UNCAUGHT EXCEPTION", exc_info=(exc_type, exc_value, exc_tb))
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _log_uncaught_exception

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # đóng cửa sổ chính = thu vào khay, không thoát app
    icon_path = resource_path("app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    app.setStyleSheet(QSS)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
