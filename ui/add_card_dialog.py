
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)

class AddCardDialog(QDialog):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("➕ Thêm thẻ mới")
        self.resize(420, 380)

        layout = QVBoxLayout()

        self.source = QComboBox()
        self.source.addItem("Tiếng Anh", "english")
        self.source.addItem("Tiếng Trung", "chinese")
        self.source.addItem("Linux", "linux")
        self.source.currentIndexChanged.connect(self._on_source_changed)

        self.front = QLineEdit()
        self.front.setPlaceholderText("hello")
        self.back = QLineEdit()
        self.back.setPlaceholderText("xin chào")
        self.pinyin = QLineEdit()
        self.pinyin.setPlaceholderText("nǐ hǎo")
        self.pronunciation = QLineEdit()
        self.pronunciation.setPlaceholderText("Nỉ hảo  (cách đọc kiểu Việt của 你好)")
        self.example = QLineEdit()
        self.example.setPlaceholderText("Hello, how are you today? (Xin chào, bạn khỏe không?)")
        self.example_pronunciation = QLineEdit()
        self.example_pronunciation.setPlaceholderText("Nỉ hảo! Hẩn cao xing... (cách đọc kiểu Việt của câu ví dụ)")
        self.options_input = QLineEdit()
        self.options_input.setPlaceholderText("-a (option1);; -b (option2)")

        self.label_pinyin = QLabel("Pinyin (chỉ cho Tiếng Trung):")
        self.label_pronunciation = QLabel("Phiên âm Việt của từ (chỉ cho Tiếng Trung):")
        self.label_example_pron = QLabel("Phiên âm Việt của câu ví dụ (chỉ cho Tiếng Trung):")

        layout.addWidget(QLabel("Nguồn:"))
        layout.addWidget(self.source)
        layout.addWidget(QLabel("Từ / lệnh:"))
        layout.addWidget(self.front)
        layout.addWidget(QLabel("Nghĩa:"))
        layout.addWidget(self.back)
        layout.addWidget(self.label_pinyin)
        layout.addWidget(self.pinyin)
        layout.addWidget(self.label_pronunciation)
        layout.addWidget(self.pronunciation)
        layout.addWidget(QLabel("Ví dụ:"))
        layout.addWidget(self.example)
        layout.addWidget(self.label_example_pron)
        layout.addWidget(self.example_pronunciation)
        layout.addWidget(QLabel("Options (;; cách nhau, chỉ cho Linux):"))
        layout.addWidget(self.options_input)

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
        self._on_source_changed()

    def _on_source_changed(self):
        is_cn = self.source.currentData() == "chinese"
        self.pinyin.setVisible(is_cn)
        self.label_pinyin.setVisible(is_cn)
        self.pronunciation.setVisible(is_cn)
        self.label_pronunciation.setVisible(is_cn)
        self.example_pronunciation.setVisible(is_cn)
        self.label_example_pron.setVisible(is_cn)

    def _save(self):
        src = self.source.currentData()
        front = self.front.text().strip()
        back = self.back.text().strip()

        if not front or not back:
            QMessageBox.warning(self, "Lỗi", "Từ và nghĩa không được để trống.")
            return

        pinyin = self.pinyin.text().strip() if src == "chinese" else ""
        pronunciation = self.pronunciation.text().strip() if src == "chinese" else ""
        example = self.example.text().strip()
        example_pronunciation = self.example_pronunciation.text().strip() if src == "chinese" else ""
        options = self.options_input.text().strip()

        new_id = self.storage.add_card(front, back, src, example, pinyin, options,
                                        pronunciation, example_pronunciation)
        if new_id is None:
            QMessageBox.critical(self, "Lỗi", "Không thể thêm card. Xem log để biết chi tiết.")
            return

        QMessageBox.information(self, "Thành công", f"Đã thêm \"{front}\" (id={new_id})")
        self.accept()
