
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
                             QLabel, QSpinBox, QPushButton, QGroupBox, QLineEdit,
                             QSlider)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("⚙️ Cài đặt")
        self.resize(380, 420)

        layout = QVBoxLayout()

        # Sources
        src_group = QGroupBox("📚 Nguồn dữ liệu")
        src_layout = QVBoxLayout()
        self.cb_english = QCheckBox("🇬🇧 Tiếng Anh")
        self.cb_chinese = QCheckBox("🀄 Tiếng Trung")
        self.cb_linux   = QCheckBox("🐧 Linux")

        enabled = storage.config.get("enabled_sources", [])
        self.cb_english.setChecked("english" in enabled)
        self.cb_chinese.setChecked("chinese" in enabled)
        self.cb_linux.setChecked("linux" in enabled)

        src_layout.addWidget(self.cb_english)
        src_layout.addWidget(self.cb_chinese)
        src_layout.addWidget(self.cb_linux)
        src_group.setLayout(src_layout)
        layout.addWidget(src_group)

        # Audio
        audio_group = QGroupBox("🔊 Âm thanh")
        audio_layout = QVBoxLayout()
        self.cb_audio = QCheckBox("Bật âm thanh (nút Nghe)")
        self.cb_audio.setChecked(storage.config.get("audio_enabled", True))
        audio_layout.addWidget(self.cb_audio)
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # Interval
        int_group = QGroupBox("⏱️ Khoảng cách mặc định (ngày cho thẻ mới)")
        int_layout = QHBoxLayout()
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 365)
        self.spin_interval.setValue(storage.config.get("default_interval", 1))
        int_layout.addWidget(QLabel("Ngày:"))
        int_layout.addWidget(self.spin_interval)
        int_layout.addStretch()
        int_group.setLayout(int_layout)
        layout.addWidget(int_group)

        # Desktop widget
        widget_group = QGroupBox("🖼️ Widget desktop")
        widget_layout = QVBoxLayout()
        self.cb_widget = QCheckBox("Hiện widget nổi trên desktop")
        self.cb_widget.setChecked(storage.config.get("desktop_widget_enabled", True))
        widget_layout.addWidget(self.cb_widget)
        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Đổi thẻ mới mỗi:"))
        self.spin_widget_interval = QSpinBox()
        self.spin_widget_interval.setRange(1, 240)
        self.spin_widget_interval.setSuffix(" phút")
        self.spin_widget_interval.setValue(storage.config.get("widget_interval_minutes", 5))
        interval_row.addWidget(self.spin_widget_interval)
        interval_row.addStretch()
        widget_layout.addLayout(interval_row)

        transparency_row = QHBoxLayout()
        self.lbl_transparency = QLabel()
        self.slider_transparency = QSlider(Qt.Orientation.Horizontal)
        self.slider_transparency.setRange(0, 90)
        self.slider_transparency.setValue(storage.config.get("widget_transparency", 35))
        self._update_transparency_label(self.slider_transparency.value())
        self.slider_transparency.valueChanged.connect(self._update_transparency_label)
        transparency_row.addWidget(QLabel("Độ trong suốt:"))
        transparency_row.addWidget(self.slider_transparency)
        transparency_row.addWidget(self.lbl_transparency)
        widget_layout.addLayout(transparency_row)

        self.cb_always_on_top = QCheckBox("Luôn hiện trên cùng (Always on Top)")
        self.cb_always_on_top.setChecked(storage.config.get("widget_always_on_top", True))
        widget_layout.addWidget(self.cb_always_on_top)

        widget_group.setLayout(widget_layout)
        layout.addWidget(widget_group)

        # AI tra cứu lệnh Linux chưa có sẵn
        ai_group = QGroupBox("🤖 Tra cứu AI cho lệnh Linux chưa có sẵn")
        ai_layout = QVBoxLayout()
        self.ai_key_input = QLineEdit()
        self.ai_key_input.setPlaceholderText("dán Groq API key vào đây (bắt đầu bằng gsk_...)")
        self.ai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.ai_key_input.setText(storage.config.get("groq_api_key", ""))
        ai_layout.addWidget(self.ai_key_input)
        ai_hint = QLabel("Lấy key miễn phí tại console.groq.com — để trống nếu không muốn dùng tính năng này.")
        ai_hint.setWordWrap(True)
        ai_hint.setStyleSheet("font-size: 11px; color: #888;")
        ai_layout.addWidget(ai_hint)
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Auto start
        auto_group = QGroupBox("🪟 Khởi động")
        auto_layout = QVBoxLayout()
        self.cb_autostart = QCheckBox("Tự động chạy cùng Windows")
        self.cb_autostart.setChecked(storage.config.get("auto_start", False))
        auto_layout.addWidget(self.cb_autostart)
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Lưu")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("Huỷ")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _update_transparency_label(self, value):
        self.lbl_transparency.setText(f"{value}%")

    def _save(self):
        sources = []
        if self.cb_english.isChecked(): sources.append("english")
        if self.cb_chinese.isChecked(): sources.append("chinese")
        if self.cb_linux.isChecked():   sources.append("linux")

        self.storage.config["enabled_sources"] = sources
        self.storage.config["audio_enabled"] = self.cb_audio.isChecked()
        self.storage.config["default_interval"] = self.spin_interval.value()
        self.storage.config["desktop_widget_enabled"] = self.cb_widget.isChecked()
        self.storage.config["widget_interval_minutes"] = self.spin_widget_interval.value()
        self.storage.config["widget_transparency"] = self.slider_transparency.value()
        self.storage.config["widget_always_on_top"] = self.cb_always_on_top.isChecked()
        self.storage.config["groq_api_key"] = self.ai_key_input.text().strip()
        self.storage.config["auto_start"] = self.cb_autostart.isChecked()
        self.storage.save_config()
        self.storage.reload_cards()

        if self.cb_autostart.isChecked():
            self._add_autostart()
        else:
            self._remove_autostart()

        self.accept()

    def _add_autostart(self):
        import sys
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "FlashcardApp", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)

    def _remove_autostart(self):
        import sys
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Run",
                                     0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "FlashcardApp")
                winreg.CloseKey(key)
            except:
                pass
