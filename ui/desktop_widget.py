
from PyQt6.QtWidgets import QWidget, QLabel, QMenu, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QGuiApplication, QAction, QCursor, QFont
from core.theme import widget_panel_colors, FG2
from ui.explain_dialog import CMDS

DEFAULT_WIDTH, DEFAULT_HEIGHT = 460, 460
MIN_WIDTH, MIN_HEIGHT = 280, 220
GRIP = 18  # kích thước vùng bắt kéo giãn ở góc dưới-phải (px)
CLICK_THRESHOLD = 6  # px — di chuyển ít hơn mức này vẫn tính là click, không phải kéo

# Màu chữ chính theo từng nguồn — dùng cho hiệu ứng 3D
FRONT_COLOR = {"english": "#4caf50", "chinese": "#ff5252", "linux": "#5b9bf5"}


def _apply_3d_effect(label, blur=14, dx=0, dy=3, alpha=210):
    """Đổ bóng phía sau chữ để tạo cảm giác nổi khối (3D/bóng bẩy) — QLabel rich
    text không hỗ trợ CSS text-shadow, nên phải dùng QGraphicsDropShadowEffect
    ở cấp widget."""
    eff = QGraphicsDropShadowEffect(label)
    eff.setBlurRadius(blur)
    eff.setOffset(dx, dy)
    eff.setColor(QColor(0, 0, 0, alpha))
    label.setGraphicsEffect(eff)


class DesktopWidget(QWidget):
    """Widget nổi, trong suốt, luôn ở trên cùng — hiện ĐẦY ĐỦ thông tin của 1
    thẻ ngay lập tức (nghĩa, phiên âm/pinyin, ví dụ, option...), chữ to, chữ
    chính có hiệu ứng đổ bóng nổi khối. Tự đổi thẻ mới sau mỗi vài phút, kéo
    thân để di chuyển, kéo góc dưới-phải (◢) để đổi kích thước, click để đổi
    thẻ ngay, bấm đúp mở cửa sổ chính. Không ghi lại review — muốn học nghiêm
    túc thì dùng cửa sổ chính."""

    def __init__(self, scheduler, storage, open_main_callback):
        super().__init__()
        self.scheduler = scheduler
        self.storage = storage
        self.open_main_callback = open_main_callback
        self.card_data = None
        self._press_global_pos = None
        self._moved_past_threshold = False
        self._resizing = False

        self.setWindowFlags(self._window_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)

        w, h = self._restore_size()
        self.resize(w, h)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)

        self.panel = QWidget(self)
        self.panel.setObjectName("desktop_widget_panel")
        self._apply_panel_style()
        # Panel + các label con phải "trong suốt với chuột" để mọi thao tác
        # (kéo di chuyển, kéo giãn, click đổi thẻ) đều tới được các hàm xử lý
        # chuột của chính DesktopWidget — nếu không, bấm trúng vùng chữ sẽ
        # không kéo/click được gì cả vì label con "ăn mất" sự kiện chuột.
        self.panel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        panel_shadow = QGraphicsDropShadowEffect(self)
        panel_shadow.setBlurRadius(28)
        panel_shadow.setOffset(0, 5)
        panel_shadow.setColor(QColor(0, 0, 0, 170))
        self.panel.setGraphicsEffect(panel_shadow)

        # Chữ chính (từ/lệnh) — to, đậm, có đổ bóng riêng cho cảm giác nổi 3D
        self.label_front = QLabel(self.panel)
        self.label_front.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_front.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.label_front.setStyleSheet("background: transparent;")
        _apply_3d_effect(self.label_front, blur=16, dy=3, alpha=220)

        # Phần chi tiết (nghĩa, phiên âm, ví dụ, option...) — chữ to rõ, đổ
        # bóng nhẹ hơn để không bị rối mắt ở đoạn nhiều chữ
        self.label_details = QLabel(self.panel)
        self.label_details.setWordWrap(True)
        self.label_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_details.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.label_details.setStyleSheet("background: transparent;")
        _apply_3d_effect(self.label_details, blur=8, dy=2, alpha=170)

        self.hint = QLabel(
            "kéo thân để di chuyển · kéo góc ◢ để đổi cỡ · click: đổi thẻ mới",
            self.panel)
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hint.setStyleSheet(f"background: transparent; font-size: 11px; color: {FG2};")

        self._resize_grip = QLabel("◢", self.panel)
        self._resize_grip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._resize_grip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._resize_grip.setStyleSheet(f"background: transparent; color: {FG2}; font-size: 15px;")

        self._layout_children()
        self._restore_position()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._auto_next)
        self._restart_timer()

        self.load_new_card()

    def _layout_children(self):
        w, h = self.width(), self.height()
        self.panel.setGeometry(0, 0, w, h)
        self.label_front.setGeometry(10, 10, w - 20, 82)
        self.label_details.setGeometry(10, 96, w - 20, h - 96 - 26)
        self.hint.setGeometry(6, h - 24, w - GRIP - 14, 18)
        self._resize_grip.setGeometry(w - GRIP - 4, h - GRIP - 4, GRIP, GRIP)

    # ---------- vị trí ----------
    def _restore_position(self):
        pos = self.storage.config.get("widget_pos")
        if pos and isinstance(pos, list) and len(pos) == 2:
            self.move(int(pos[0]), int(pos[1]))
            return
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 24)

    def _save_position(self):
        p = self.pos()
        self.storage.config["widget_pos"] = [p.x(), p.y()]
        self.storage.save_config()

    # ---------- kích thước ----------
    def _restore_size(self):
        size = self.storage.config.get("widget_size")
        if size and isinstance(size, list) and len(size) == 2:
            return max(MIN_WIDTH, int(size[0])), max(MIN_HEIGHT, int(size[1]))
        return DEFAULT_WIDTH, DEFAULT_HEIGHT

    def _save_size(self):
        self.storage.config["widget_size"] = [self.width(), self.height()]
        self.storage.save_config()

    # ---------- giao diện: trong suốt + luôn-trên-cùng (đổi được trong Cài đặt) ----------
    def _window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.storage.config.get("widget_always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        return flags

    def _apply_panel_style(self):
        transparency = self.storage.config.get("widget_transparency", 35)
        bg, border = widget_panel_colors(transparency)
        self.panel.setStyleSheet(
            f"#desktop_widget_panel {{"
            f"background-color: {bg};"
            f"border: 1px solid {border};"
            f"border-radius: 16px;"
            f"}}"
        )

    # ---------- hẹn giờ đổi thẻ ----------
    def _restart_timer(self):
        minutes = self.storage.config.get("widget_interval_minutes", 5) or 5
        self.timer.start(int(minutes) * 60 * 1000)

    def _auto_next(self):
        self.load_new_card()

    # ---------- nội dung thẻ ----------
    def load_new_card(self):
        self.card_data = self.scheduler.get_next_card()
        self._render()

    def _render(self):
        if not self.card_data:
            self.label_front.setText("😴")
            self.label_details.setText(
                "<div style='text-align:center;font-size:18px;'>Không có thẻ nào.<br>"
                "Bật nguồn dữ liệu trong Cài đặt.</div>"
            )
            return
        d = self.card_data
        src = d.get("source", "")
        front = d.get("front", "?")
        back = (d.get("back", "") or "").replace("\n", "<br>")
        color = FRONT_COLOR.get(src, "#ffffff")

        if src == "chinese":
            front_html, details_html = self._render_chinese(d, front, back, color)
        elif src == "linux":
            front_html, details_html = self._render_linux(d, front, back, color)
        else:
            front_html, details_html = self._render_english(d, front, back, color)

        self.label_front.setText(front_html)
        self.label_details.setText(details_html)

    @staticmethod
    def _render_english(d, front, back, color):
        example = d.get("example", "")
        front_html = (
            f"<div style='text-align:center;'>"
            f"<b style='font-size:56px;color:{color};'>{front}</b>"
            f"</div>"
        )
        details = f"<div style='text-align:center;'><span style='font-size:26px;'>{back}</span>"
        if example:
            details += f"<br><br><span style='font-size:18px;color:#bbb;'><i>{example}</i></span>"
        details += "</div>"
        return front_html, details

    @staticmethod
    def _render_chinese(d, front, back, color):
        pinyin = d.get("pinyin", "")
        pron = d.get("pronunciation", "")
        example = d.get("example", "")
        ex_pron = d.get("example_pronunciation", "")
        front_html = (
            f"<div style='text-align:center;'>"
            f"<b style='font-size:58px;color:{color};'>{front}</b>"
            f"</div>"
        )
        # Phiên âm (pinyin + phiên âm Việt) đặt NGAY DƯỚI chữ học, phía trên nghĩa
        pron_line = " · ".join(p for p in (pinyin, pron) if p)
        details = "<div style='text-align:center;'>"
        if pron_line:
            details += f"<span style='font-size:19px;color:#ccc;'>{pron_line}</span><br>"
        details += f"<span style='font-size:26px;'>{back}</span>"
        if example:
            details += f"<br><br><span style='font-size:17px;color:#bbb;'>{example}</span>"
        if ex_pron:
            details += f"<br><span style='font-size:16px;color:#999;'><i>{ex_pron}</i></span>"
        details += "</div>"
        return front_html, details

    @staticmethod
    def _render_linux(d, front, back, color):
        options_raw = d.get("options", "")
        opts_html = ""
        if options_raw and options_raw != "(không có option phổ biến)":
            opts = [o.strip() for o in options_raw.split(";;") if o.strip()]
            if opts:
                opts_html = "<br>".join(
                    f"<span style='font-size:17px;color:#ddd;'>{o}</span>" for o in opts
                )

        cmd_info = CMDS.get(front)
        ex_html = ""
        example_field = d.get("example", "")
        if cmd_info and cmd_info.get("examples"):
            rows = [f"$ {c}" for c, desc, out in cmd_info["examples"][:2]]
            ex_html = "<br>".join(
                f"<span style='font-size:17px;color:#8fd18f;'>{r}</span>" for r in rows
            )
        elif example_field:
            ex_html = f"<span style='font-size:17px;color:#8fd18f;'>{example_field}</span>"

        front_html = (
            f"<div style='text-align:center;'>"
            f"<b style='font-size:52px;color:{color};'>{front}</b>"
            f"</div>"
        )
        details = f"<div style='text-align:center;'><span style='font-size:23px;'>{back}</span>"
        if opts_html:
            details += f"<br><br><span style='font-size:16px;color:#ffa726;font-weight:bold;'>▸ Tuỳ chọn:</span><br>{opts_html}"
        if ex_html:
            details += f"<br><br><span style='font-size:16px;color:#ffa726;font-weight:bold;'>▸ Ví dụ:</span><br>{ex_html}"
        details += "</div>"
        return front_html, details

    # ---------- chuột: kéo thả + kéo giãn + click lật + menu phải-chuột ----------
    def _in_grip_area(self, pos):
        return (self.width() - pos.x()) <= (GRIP + 8) and (self.height() - pos.y()) <= (GRIP + 8)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            pos = e.position().toPoint()
            if self._in_grip_area(pos):
                self._resizing = True
                wh = self.windowHandle()
                if wh is not None:
                    wh.startSystemResize(Qt.Edge.RightEdge | Qt.Edge.BottomEdge)
            else:
                # CHƯA giao cho window manager ngay — chỉ ghi nhận điểm bấm.
                # Nếu giao ngay (startSystemMove ngay lúc press), một cú
                # click đơn thuần (không kéo) cũng bị WM "nuốt" mất, sự kiện
                # thả chuột (mouseReleaseEvent) nhiều khi không quay lại được
                # ứng dụng nữa — khiến click không còn đổi được thẻ mới. Chỉ
                # thật sự bắt đầu kéo (gọi startSystemMove) khi di chuyển vượt
                # quá một ngưỡng nhỏ, ở mouseMoveEvent bên dưới.
                self._press_global_pos = e.globalPosition().toPoint()
                self._moved_past_threshold = False
        elif e.button() == Qt.MouseButton.RightButton:
            self._show_menu(e.globalPosition().toPoint())

    def mouseMoveEvent(self, e):
        if self._resizing:
            return
        if self._press_global_pos is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            delta = e.globalPosition().toPoint() - self._press_global_pos
            if not self._moved_past_threshold and (abs(delta.x()) > CLICK_THRESHOLD or abs(delta.y()) > CLICK_THRESHOLD):
                self._moved_past_threshold = True
                wh = self.windowHandle()
                if wh is not None:
                    wh.startSystemMove()
            return
        # Hover (không bấm giữ gì cả): đổi con trỏ khi ở gần góc kéo giãn
        if self._in_grip_area(e.position().toPoint()):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        if self._resizing:
            self._resizing = False
            return  # kích thước mới đã được lưu tự động qua resizeEvent()
        if self._press_global_pos is not None:
            moved = self._moved_past_threshold
            self._press_global_pos = None
            self._moved_past_threshold = False
            if not moved:
                self.load_new_card()
            # Nếu có kéo (moved=True): vị trí mới đã được lưu tự động qua
            # moveEvent() bên dưới — không phụ thuộc việc mouseReleaseEvent
            # có quay lại được ứng dụng hay không sau khi giao cho WM.

    def moveEvent(self, e):
        super().moveEvent(e)
        self._save_position()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._layout_children()
        self._save_size()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.open_main_callback:
            self.open_main_callback()

    def _show_menu(self, global_pos):
        menu = QMenu(self)
        act_new = QAction("🔄 Đổi thẻ ngay", self)
        act_new.triggered.connect(self.load_new_card)
        act_main = QAction("🗔 Mở cửa sổ chính", self)
        act_main.triggered.connect(lambda: self.open_main_callback() if self.open_main_callback else None)
        act_reset_size = QAction("↔️ Về kích thước mặc định", self)
        act_reset_size.triggered.connect(self._reset_size)
        act_reset_pos = QAction("📍 Về vị trí mặc định (góc dưới-phải)", self)
        act_reset_pos.triggered.connect(self._reset_position)
        act_hide = QAction("🙈 Ẩn widget", self)
        act_hide.triggered.connect(self.hide)
        menu.addAction(act_new)
        menu.addAction(act_main)
        menu.addAction(act_reset_size)
        menu.addAction(act_reset_pos)
        menu.addSeparator()
        menu.addAction(act_hide)
        menu.exec(global_pos)

    def _reset_size(self):
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self._save_size()

    def _reset_position(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 24)
        self._save_position()

    def apply_settings(self):
        """Gọi lại sau khi đổi cài đặt (khoảng thời gian đổi thẻ, độ trong
        suốt, luôn-trên-cùng...)."""
        self._restart_timer()
        self._apply_panel_style()

        # Đổi windowFlags trên 1 cửa sổ ĐANG HIỆN đôi khi không đủ để Windows
        # thực sự cập nhật thuộc tính "topmost" ở tầng hệ điều hành — dù gọi
        # setWindowFlags() xong show() lại, cửa sổ có thể vẫn giữ trạng thái
        # topmost cũ (từng gặp vấn đề tương tự với việc kéo thả trước đây).
        # Cách chắc chắn hơn: ẩn hẳn cửa sổ trước, để Qt/hệ điều hành thực sự
        # phá huỷ và tạo lại cửa sổ với cờ mới, rồi mới hiện lại.
        was_visible = self.isVisible()
        pos, size = self.pos(), self.size()
        self.hide()
        self.setWindowFlags(self._window_flags())
        self.resize(size)
        self.move(pos)
        if was_visible:
            self.show()
