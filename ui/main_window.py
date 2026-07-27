
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon, QAction
from ui.flashcard import FlashCard
from ui.settings_dialog import SettingsDialog
from ui.add_card_dialog import AddCardDialog
from ui.quiz_dialog import QuizDialog
from ui.stats_dialog import StatsDialog
from ui.favorites_dialog import FavoritesDialog
from ui.explain_dialog import ExplainDialog
from ui.cheat_dialog import CheatDialog
from ui.desktop_widget import DesktopWidget
from core.scheduler import Scheduler
from core.storage import Storage
from core.audio import speak_sequence
from core.stats import calc_streak
from core.paths import resource_path
import datetime

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.storage = Storage()
        self.scheduler = Scheduler(self.storage)

        n_en = sum(1 for c in self.storage.cards if c.get("source") == "english")
        n_cn = sum(1 for c in self.storage.cards if c.get("source") == "chinese")
        n_lnx = sum(1 for c in self.storage.cards if c.get("source") == "linux")
        self.setWindowTitle(f"🇬🇧{n_en} 🀄{n_cn} 🐧{n_lnx} — Flashcard")

        top = QHBoxLayout()
        self.btn_en = QPushButton("🇬🇧 Anh")
        self.btn_cn = QPushButton("🀄 Trung")
        self.btn_lnx = QPushButton("🐧 Linux")
        for b in [self.btn_en, self.btn_cn, self.btn_lnx]:
            b.setObjectName("btn_source")
            b.setProperty("active", "false")
        self.btn_en.clicked.connect(lambda: self._toggle_source("english"))
        self.btn_cn.clicked.connect(lambda: self._toggle_source("chinese"))
        self.btn_lnx.clicked.connect(lambda: self._toggle_source("linux"))
        top.addWidget(self.btn_en)
        top.addWidget(self.btn_cn)
        top.addWidget(self.btn_lnx)
        top.addStretch()
        self.btn_add = QPushButton("➕ Thêm")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.clicked.connect(self._open_add_dialog)
        top.addWidget(self.btn_add)
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.clicked.connect(self._open_settings)
        top.addWidget(self.btn_settings)

        tools = QHBoxLayout()
        for text, handler in [
            ("🎯 Trắc nghiệm", self._open_quiz),
            ("⭐ Yêu thích", self._open_favorites),
            ("📊 Thống kê", self._open_stats),
            ("❓ Giải thích", self._open_explain),
            ("📋 Tra nhanh", self._open_cheat),
        ]:
            btn = QPushButton(text)
            btn.setObjectName("tool_btn")
            btn.clicked.connect(handler)
            tools.addWidget(btn)
        tools.addStretch()

        self.card = FlashCard(self._speak, self._toggle_favorite, self._on_card_answer)

        self.status = QLabel()
        self.status.setObjectName("status_label")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tracking = QLabel()
        self.tracking.setObjectName("tracking_label")
        self.tracking.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(tools)
        layout.addWidget(self.card)
        layout.addWidget(self.status)
        layout.addWidget(self.tracking)
        self.setLayout(layout)

        QShortcut(QKeySequence("Ctrl+Alt+N"), self).activated.connect(self.load_next)
        QShortcut(QKeySequence("Ctrl+Alt+S"), self).activated.connect(self._speak_current)
        QShortcut(QKeySequence("Space"), self).activated.connect(self.card.flip)

        self._sync_button_styles()
        self.load_next()

        # Kích thước cửa sổ tính theo nội dung thật (sizeHint) thay vì số cố
        # định — trước đây resize(960,700) từng nhỏ hơn nội dung thật cần
        # (~815x804), khiến cửa sổ mở lên bị cắt, phải tự kéo giãn mới thấy hết.
        hint = self.sizeHint()
        self.setMinimumSize(700, 600)
        self.resize(max(960, hint.width() + 40), max(760, hint.height() + 40))

        self._really_quit = False
        self.desktop_widget = DesktopWidget(self.scheduler, self.storage, self.show_main)
        if self.storage.config.get("desktop_widget_enabled", True):
            self.desktop_widget.show()

        self._setup_tray()

    def _icon_path(self):
        path = resource_path("app_icon.png")
        return path if os.path.exists(path) else None

    def _setup_tray(self):
        icon_path = self._icon_path()
        icon = QIcon(icon_path) if icon_path else self.style().standardIcon(
            self.style().StandardPixmap.SP_ComputerIcon)
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Flashcard — đang chạy trong khay hệ thống")

        menu = QMenu()
        act_show = QAction("🗔 Hiện cửa sổ chính", self)
        act_show.triggered.connect(self.show_main)
        menu.addAction(act_show)

        self.act_widget = QAction("🖼️ Ẩn widget desktop", self)
        self.act_widget.triggered.connect(self._toggle_widget)
        self._sync_widget_action_text()
        menu.addAction(self.act_widget)

        act_settings = QAction("⚙️ Cài đặt", self)
        act_settings.triggered.connect(self._open_settings)
        menu.addAction(act_settings)

        menu.addSeparator()
        act_quit = QAction("❌ Thoát", self)
        act_quit.triggered.connect(self._quit_app)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_main()

    def show_main(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _sync_widget_action_text(self):
        visible = self.desktop_widget.isVisible() if hasattr(self, "desktop_widget") else True
        self.act_widget.setText("🖼️ Ẩn widget desktop" if visible else "🖼️ Hiện widget desktop")

    def _toggle_widget(self):
        if self.desktop_widget.isVisible():
            self.desktop_widget.hide()
        else:
            self.desktop_widget.show()
        self.storage.config["desktop_widget_enabled"] = self.desktop_widget.isVisible()
        self.storage.save_config()
        self._sync_widget_action_text()

    def closeEvent(self, event):
        if self._really_quit:
            event.accept()
            return
        event.ignore()
        self.hide()
        if not self.storage.config.get("_da_bao_thu_gon", False):
            self.tray.showMessage(
                "Flashcard vẫn đang chạy",
                "Ứng dụng thu gọn vào khay hệ thống, không thoát hẳn. "
                "Click phải vào icon khay để Thoát hẳn.",
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )
            self.storage.config["_da_bao_thu_gon"] = True
            self.storage.save_config()

    def _quit_app(self):
        from PyQt6.QtWidgets import QApplication
        self._really_quit = True
        self.desktop_widget.close()
        self.tray.hide()
        QApplication.instance().quit()

    def _sync_button_styles(self):
        enabled = self.storage.config.get("enabled_sources", [])
        for s, b in [("english", self.btn_en), ("chinese", self.btn_cn), ("linux", self.btn_lnx)]:
            active = "true" if s in enabled else "false"
            b.setProperty("active", active)
            b.style().unpolish(b)
            b.style().polish(b)

    def _toggle_source(self, source):
        enabled = self.storage.config.get("enabled_sources", [])

        if source not in enabled:
            new_enabled = enabled + [source]
        elif len(enabled) == 1 and source in enabled:
            new_enabled = ["english", "chinese", "linux"]
        else:
            new_enabled = [source]

        self.storage.config["enabled_sources"] = new_enabled
        self.storage.save_config()
        self.storage.reload_cards()
        self.scheduler = Scheduler(self.storage)
        self._update_title()
        self._sync_button_styles()
        self.load_next()
        if hasattr(self, "desktop_widget"):
            self.desktop_widget.scheduler = self.scheduler

    def _update_title(self):
        n_en = sum(1 for c in self.storage.cards if c.get("source") == "english")
        n_cn = sum(1 for c in self.storage.cards if c.get("source") == "chinese")
        n_lnx = sum(1 for c in self.storage.cards if c.get("source") == "linux")
        self.setWindowTitle(f"🇬🇧{n_en} 🀄{n_cn} 🐧{n_lnx} — Flashcard")

    def load_next(self):
        item = self.scheduler.get_next_card()
        if item:
            self.card.set_data(item)
        self._update_status()

    def _update_status(self):
        total = len(self.storage.cards)
        today = str(datetime.date.today())
        due = sum(1 for c in self.storage.cards if c["next_review"] <= today)
        self.status.setText(f"📚 {total} thẻ  ·  📅 Cần ôn: {due}")

        learned = sum(1 for c in self.storage.cards if c["next_review"] > "2000-01-10")
        streak = calc_streak(self.storage.get_review_log(365))
        self.tracking.setText(f"👤 User  ·  ✅ Đã học: {learned}  ·  🔥 Chuỗi: {streak} ngày")

    def _on_card_answer(self, action):
        card = self.card.data
        if not card:
            return
        if action == "_next":
            self.load_next()
            return
        # Ghi nhận kết quả SRS ngay lúc kiểm tra/bỏ qua, nhưng KHÔNG đổi thẻ ở
        # đây — nếu đổi ngay, phần phản hồi đúng/sai vừa hiện ra (trong
        # FlashCard._check_practice) sẽ bị ghi đè mất trước khi người dùng kịp
        # đọc, vì set_data() của thẻ mới sẽ reset toàn bộ khung phản hồi. Chỉ
        # đổi thẻ khi người dùng bấm "Tiếp →" (action == "_next" ở trên).
        self.scheduler.review(action, card)
        self.storage.log_review(card.get("id", -1), action, card.get("source", ""))
        self.storage.save()
        self._update_status()

    def _toggle_favorite(self, data):
        cid = data.get("id", -1)
        if cid < 0:
            return
        result = self.storage.toggle_favorite(cid)
        if result is not None:
            data["favorite"] = 1 if result else 0

    def _speak(self, data):
        if not self.storage.config.get("audio_enabled", True):
            return
        source = data.get("source", "")
        front = data.get("front", "")
        back = data.get("back", "")
        example = data.get("example", "")

        segments = []
        if source == "english":
            segments.append((front, "en"))
            segments.append((f"Nghĩa: {back}", "vi"))
            if example:
                en_part, vi_part = self._split_example(example)
                if en_part:
                    segments.append((en_part, "en"))
                if vi_part:
                    segments.append((vi_part, "vi"))
        elif source == "chinese":
            segments.append((front, "zh"))
            segments.append((f"Nghĩa: {back}", "vi"))
            cn_part, vi_part = self._split_example(example)
            if cn_part:
                segments.append((cn_part, "zh"))
            if vi_part:
                segments.append((vi_part, "vi"))
        elif source == "linux":
            segments.append((f"Lệnh {front}. {back}", "vi"))
            if example:
                segments.append((example, "vi"))
        else:
            segments.append((front, "vi"))

        speak_sequence(segments)

    def _speak_current(self):
        if self.card.data and self.storage.config.get("audio_enabled", True):
            self._speak(self.card.data)

    @staticmethod
    def _split_example(text):
        if not text or "(" not in text:
            return text, None
        start = text.find("(")
        end = text.rfind(")")
        cn_part = text[:start].strip()
        vi_part = text[start+1:end].strip() if start < end else None
        return cn_part, vi_part

    def _open_add_dialog(self):
        dlg = AddCardDialog(self.storage, self)
        if dlg.exec() == AddCardDialog.DialogCode.Accepted:
            self.storage.reload_cards()
            self.scheduler = Scheduler(self.storage)
            self._update_title()
            self.load_next()
            if hasattr(self, "desktop_widget"):
                self.desktop_widget.scheduler = self.scheduler

    def _open_settings(self):
        dlg = SettingsDialog(self.storage, self)
        if dlg.exec() == SettingsDialog.DialogCode.Accepted:
            self.storage.reload_cards()
            self.scheduler = Scheduler(self.storage)
            self._update_title()
            self._sync_button_styles()
            self.load_next()
            self.desktop_widget.scheduler = self.scheduler
            self.desktop_widget.apply_settings()
            if self.storage.config.get("desktop_widget_enabled", True):
                self.desktop_widget.show()
            else:
                self.desktop_widget.hide()
            self._sync_widget_action_text()

    def _open_quiz(self):
        dlg = QuizDialog(self.storage.get_all_cards(), self.storage, self)
        dlg.exec()
        self.load_next()

    def _open_stats(self):
        dlg = StatsDialog(self.storage, self)
        dlg.exec()

    def _open_favorites(self):
        dlg = FavoritesDialog(self.storage, self)
        if dlg.exec() == FavoritesDialog.DialogCode.Accepted:
            self.storage.reload_cards()
            self.scheduler = Scheduler(self.storage)
            self.load_next()
            if hasattr(self, "desktop_widget"):
                self.desktop_widget.scheduler = self.scheduler

    def _open_explain(self):
        dlg = ExplainDialog(self.storage, self)
        dlg.exec()

    def _open_cheat(self):
        dlg = CheatDialog(self)
        dlg.exec()
