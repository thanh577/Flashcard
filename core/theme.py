
BG = "#1a1a2e"
BG2 = "#16213e"
BG_CARD = "#1e1e3a"
BG_INPUT = "#0f0f23"
FG = "#e0e0e0"
FG2 = "#888"
FG3 = "#aaa"
ACCENT = "#ffa726"
GREEN = "#4caf50"
RED = "#f44336"
BLUE = "#42a5f5"
CYAN = "#80cbc4"
BORDER = "#3a3a5a"
BORDER_HI = "#6a6a8a"
BG_BTN = "#2a2a4a"
BG_BTN_HOVER = "#3a3a5a"
BG_BTN_PRESSED = "#4a4a6a"
GOLD = "#ffd700"
BG_CORRECT = "#1a3a1a"
BG_WRONG = "#3a1a1a"

# Widget desktop trong suốt — màu nền/viền gốc (chưa gồm alpha, alpha tính
# động theo mức "độ trong suốt" người dùng chọn trong Cài đặt)
WIDGET_BG_RGB = (26, 26, 46)
WIDGET_BORDER_RGB = (136, 136, 170)


def widget_panel_colors(transparency_pct=35):
    """Tính màu nền/viền dạng rgba(...) theo % độ trong suốt (0=đục hoàn
    toàn, 90=rất trong suốt). Có sàn tối thiểu alpha=25 để không bao giờ
    biến mất hoàn toàn (không thấy được viền/chữ nữa)."""
    t = max(0, min(90, transparency_pct))
    bg_alpha = max(25, round(255 * (1 - t / 100)))
    border_alpha = max(30, round(230 * (1 - t / 100)))
    bg = f"rgba({WIDGET_BG_RGB[0]}, {WIDGET_BG_RGB[1]}, {WIDGET_BG_RGB[2]}, {bg_alpha})"
    border = f"rgba({WIDGET_BORDER_RGB[0]}, {WIDGET_BORDER_RGB[1]}, {WIDGET_BORDER_RGB[2]}, {border_alpha})"
    return bg, border

# Giữ 2 hằng số cũ (mức trong suốt mặc định 35%) để không phá vỡ chỗ nào lỡ
# import trực tiếp — nhưng ui/desktop_widget.py giờ dùng widget_panel_colors()
WIDGET_BG, WIDGET_BORDER = widget_panel_colors(35)

FONT_XS = "14px"
FONT_SM = "18px"
FONT_BASE = "22px"
FONT_LG = "28px"
FONT_XL = "40px"
FONT_2XL = "62px"
FONT_3XL = "96px"
FONT_DISPLAY = "144px"

QSS = f"""
QWidget {{
    background-color: {BG};
    color: {FG};
    font-size: {FONT_SM};
}}

QPushButton {{
    background-color: {BG_BTN};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    color: {FG};
}}
QPushButton:hover {{
    background-color: {BG_BTN_HOVER};
    border: 1px solid {BORDER_HI};
}}
QPushButton:pressed {{
    background-color: {BG_BTN_PRESSED};
}}
QPushButton:disabled {{
    color: #555;
    background-color: {BG};
}}

QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {FG};
}}
QLineEdit:focus {{
    border: 1px solid {BORDER_HI};
}}

QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG};
    border-radius: 6px;
}}
QTabBar::tab {{
    background-color: {BG_BTN};
    border: 1px solid {BORDER};
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {BG};
    border-bottom-color: {BG};
}}

QScrollArea {{
    border: none;
}}
QScrollBar:vertical {{
    background-color: {BG};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background-color: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: #5a5a7a;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QTableWidget {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: #2a2a4a;
}}
QHeaderView::section {{
    background-color: {BG_BTN};
    border: 1px solid {BORDER};
    padding: 6px;
    font-weight: bold;
}}

QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {FG};
    background-color: {BG_INPUT};
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 4px;
}}

QComboBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
}}
QComboBox:focus {{
    border: 1px solid {BORDER_HI};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {BG};
    border: 1px solid {BORDER};
    selection-background-color: {BG_BTN_HOVER};
}}

QListWidget {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QListWidget::item:selected {{
    background-color: {BG_BTN_HOVER};
}}
QListWidget::item:hover {{
    background-color: {BG_BTN};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}

QSpinBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
}}

QLabel {{
    background-color: transparent;
}}

QMessageBox {{
    background-color: {BG};
}}
QMessageBox QLabel {{
    color: {FG};
}}

/* ===== FlashCard (thẻ bài) ===== */
#FlashCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 8px;
}}

#card_label {{
    background-color: transparent;
    font-size: {FONT_BASE};
    padding: 24px;
    min-height: 180px;
}}

/* Thẻ bài — nút nghe */
#btn_speak {{
    font-size: 30px;
    padding: 8px 16px;
}}

/* Thẻ bài — nút yêu thích */
#btn_fav {{
    font-size: {FONT_XL};
    padding: 6px 16px;
}}

/* Thẻ bài — ô nhập */
#practice_input {{
    font-size: {FONT_LG};
    padding: 10px;
}}

/* Thẻ bài — nút Kiểm tra/Bỏ qua/Tiếp/Lệnh tiếp theo (Linux) */
#btn_check, #btn_skip, #btn_next, #btn_linux_next {{
    font-size: {FONT_BASE};
    padding: 8px 18px;
}}

/* Thẻ bài — nhắc nhở gõ */
#practice_prompt {{
    font-size: {FONT_BASE};
    color: {ACCENT};
    font-weight: bold;
}}

/* Thẻ bài — phản hồi */
#practice_feedback {{
    font-size: {FONT_BASE};
    padding: 8px;
}}

/* ===== Main window ===== */
/* Nút nguồn (Anh / Trung / Linux) */
#btn_source {{
    font-size: {FONT_BASE};
    padding: 6px 14px;
    border-radius: 6px;
}}
#btn_source[active="true"] {{
    background-color: {BG_BTN_HOVER};
    border: 2px solid {BORDER_HI};
    font-weight: bold;
}}

/* Nút thêm / cài đặt trên cùng */
#btn_add, #btn_settings {{
    font-size: {FONT_BASE};
    padding: 6px 14px;
}}

/* Nút công cụ (Quiz, Yêu thích, ...) */
#tool_btn {{
    font-size: 20px;
    padding: 6px 12px;
}}

/* Thanh trạng thái */
#status_label, #tracking_label {{
    color: {FG2};
    font-size: {FONT_BASE};
}}
"""
