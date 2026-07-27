
import random
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QProgressBar, QComboBox)
from PyQt6.QtCore import Qt


class PracticeDialog(QDialog):
    def __init__(self, cards, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("✍️ Luyện viết")
        self.resize(540, 420)

        self.all_cards = [c for c in cards if c.get("id", -1) > 0]
        self.storage_ref = storage
        self.index = 0
        self.correct = 0
        self.card_list = []
        self.total = 0

        layout = QVBoxLayout()

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Chế độ:"))
        self.mode = QComboBox()
        self.mode.addItem("📝 Nghĩa (tất cả)", "meaning")
        self.mode.addItem("🀄 Pinyin (Tiếng Trung)", "pinyin")
        self.mode.currentIndexChanged.connect(self._rebuild)
        mode_row.addWidget(self.mode)
        mode_row.addStretch()
        self.count_label = QLabel()
        self.count_label.setStyleSheet("font-size: 16px; color: #888;")
        mode_row.addWidget(self.count_label)
        layout.addLayout(mode_row)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.prompt_label = QLabel("...")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setStyleSheet("font-size: 36px; padding: 20px;")
        layout.addWidget(self.prompt_label)

        self.hint_label = QLabel()
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 18px; color: #888; padding: 4px;")
        layout.addWidget(self.hint_label)

        self.input_box = QLineEdit()
        self.input_box.setStyleSheet("font-size: 28px; padding: 12px;")
        self.input_box.returnPressed.connect(self._check)
        layout.addWidget(self.input_box)

        btn_row = QHBoxLayout()
        self.btn_check = QPushButton("✅ Kiểm tra")
        self.btn_check.setStyleSheet("font-size: 22px; padding: 10px;")
        self.btn_check.clicked.connect(self._check)
        btn_row.addWidget(self.btn_check)

        self.btn_skip = QPushButton("⏭ Bỏ qua")
        self.btn_skip.setStyleSheet("font-size: 22px; padding: 10px;")
        self.btn_skip.clicked.connect(self._skip)
        btn_row.addWidget(self.btn_skip)

        self.btn_next = QPushButton("Tiếp →")
        self.btn_next.setStyleSheet("font-size: 22px; padding: 10px;")
        self.btn_next.setVisible(False)
        self.btn_next.clicked.connect(self._next)
        btn_row.addWidget(self.btn_next)
        layout.addLayout(btn_row)

        self.feedback = QLabel()
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback.setStyleSheet("font-size: 20px; padding: 12px;")
        layout.addWidget(self.feedback)

        self.setLayout(layout)
        self._rebuild()

    def _rebuild(self):
        mode = self.mode.currentData()
        if mode == "pinyin":
            self.card_list = [c for c in self.all_cards
                              if c.get("source") == "chinese" and c.get("pinyin")]
        else:
            self.card_list = list(self.all_cards)
        random.shuffle(self.card_list)
        self.index = 0
        self.correct = 0
        self.total = min(len(self.card_list), 30)
        self.progress.setMaximum(self.total)
        self.count_label.setText(f"/ {len(self.card_list)} thẻ")
        self._show_card()

    def _show_card(self):
        if self.index >= self.total:
            self._finish()
            return

        card = self.card_list[self.index]
        self.current_card = card
        self.input_box.setEnabled(True)
        self.input_box.clear()
        self.input_box.setFocus()
        self.btn_check.setVisible(True)
        self.btn_skip.setVisible(True)
        self.btn_next.setVisible(False)
        self.feedback.setText("")
        self.input_box.setStyleSheet("font-size: 28px; padding: 12px;")
        self.answered = False

        src = card.get("source", "")
        tag = {"english": "🇬🇧", "chinese": "🀄", "linux": "🐧"}.get(src, "")
        self.prompt_label.setText(f"{tag}  {card['front']}")

        mode = self.mode.currentData()
        if mode == "pinyin":
            self.hint_label.setText("Gõ pinyin (có dấu hoặc không dấu)")
        elif src == "chinese":
            py = card.get("pinyin", "")
            self.hint_label.setText(f"Gợi ý: pinyin = {py}" if py else "")
        else:
            self.hint_label.setText("")

        self.progress.setValue(self.index)

    def _get_correct(self):
        mode = self.mode.currentData()
        card = self.current_card
        if mode == "pinyin":
            return card.get("pinyin", card["back"])
        return card["back"]

    def _check(self):
        if self.answered:
            return
        self.answered = True
        card = self.current_card
        correct = self._get_correct()
        user_answer = self.input_box.text().strip().lower()
        is_correct = self._normalize(user_answer) == self._normalize(correct)

        if is_correct:
            self.correct += 1
            self.feedback.setStyleSheet("font-size: 22px; color: #4caf50; padding: 12px;")
            self.feedback.setText(f"✅ Đúng! → {correct}")
            self.input_box.setStyleSheet("font-size: 28px; padding: 12px; background-color: #1a3a1a;")
            self.storage_ref.log_review(card["id"], "good", card.get("source", ""))
        else:
            self.feedback.setStyleSheet("font-size: 22px; color: #f44336; padding: 12px;")
            self.feedback.setText(f"❌ Sai. Đáp án: {correct}")
            self.input_box.setStyleSheet("font-size: 28px; padding: 12px; background-color: #3a1a1a;")
            self.storage_ref.log_review(card["id"], "again", card.get("source", ""))

        example = card.get("example", "")
        if example:
            self.feedback.setText(self.feedback.text() + f"\n\nVí dụ: {example}")

        self.input_box.setEnabled(False)
        self.btn_check.setVisible(False)
        self.btn_skip.setVisible(False)
        self.btn_next.setVisible(True)
        self.btn_next.setFocus()

    def _skip(self):
        self.answered = True
        correct = self._get_correct()
        self.feedback.setStyleSheet("font-size: 22px; color: #ffa726; padding: 12px;")
        self.feedback.setText(f"⏭ Đáp án: {correct}")
        self.input_box.setEnabled(False)
        self.btn_check.setVisible(False)
        self.btn_skip.setVisible(False)
        self.btn_next.setVisible(True)
        self.btn_next.setFocus()

    def _next(self):
        self.index += 1
        self._show_card()

    def _finish(self):
        pct = int(self.correct / self.total * 100) if self.total else 0
        self.prompt_label.setText("✍️ Hoàn thành!")
        self.hint_label.setText("")
        self.input_box.setVisible(False)
        self.btn_check.setVisible(False)
        self.btn_skip.setVisible(False)
        self.btn_next.setVisible(False)
        self.feedback.setStyleSheet("font-size: 28px; padding: 16px; color: #4caf50;")
        self.feedback.setText(f"{self.correct}/{self.total} đúng ({pct}%)")

        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("font-size: 24px; padding: 12px; margin-top: 16px;")
        close_btn.clicked.connect(self.accept)
        self.layout().addWidget(close_btn)

    @staticmethod
    def _normalize(s):
        import re
        s = s.strip().lower()
        s = re.sub(r'\s+', ' ', s)
        s = s.replace('/', ' / ')
        s = re.sub(r'\s+', ' ', s).strip()
        return s
