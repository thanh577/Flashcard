
import random
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar)
from PyQt6.QtCore import Qt, QTimer

class QuizDialog(QDialog):
    def __init__(self, cards, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("🎯 Trắc nghiệm")
        self.resize(500, 350)

        self.cards = [c for c in cards if c.get("id", -1) > 0]
        random.shuffle(self.cards)
        self.index = 0
        self.correct = 0
        self.total = min(len(self.cards), 20)

        layout = QVBoxLayout()

        self.progress = QProgressBar()
        self.progress.setMaximum(self.total)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.q_label = QLabel("...")
        self.q_label.setWordWrap(True)
        self.q_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.q_label.setStyleSheet("font-size: 36px; padding: 20px;")
        layout.addWidget(self.q_label)

        self.btn_group = QVBoxLayout()
        self.buttons = []
        for i in range(4):
            btn = QPushButton()
            btn.setStyleSheet("font-size: 24px; padding: 12px; text-align: left;")
            btn.clicked.connect(lambda checked, b=btn: self._check(b))
            self.buttons.append(btn)
            self.btn_group.addWidget(btn)
        layout.addLayout(self.btn_group)

        self.feedback = QLabel()
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback.setStyleSheet("font-size: 20px; padding: 8px;")
        layout.addWidget(self.feedback)

        self.setLayout(layout)
        self._next_question()

    def _next_question(self):
        if self.index >= self.total:
            self._finish()
            return

        card = self.cards[self.index]
        self.q_label.setText(card["front"])
        self.current_card = card
        self.feedback.setText("")
        self.answered = False

        correct = card["back"]
        wrong_pool = [c["back"] for c in self.cards if c["back"] != correct]
        options = [correct] + random.sample(wrong_pool, min(3, len(wrong_pool)))
        random.shuffle(options)

        for i, opt in enumerate(options):
            self.buttons[i].setText(f"{i+1}. {opt}")
            self.buttons[i].setEnabled(True)
            self.buttons[i].setStyleSheet(
                "font-size: 24px; padding: 12px; text-align: left;"
            )

        self.progress.setValue(self.index)

    def _check(self, btn):
        if self.answered:
            return
        self.answered = True
        correct = self.current_card["back"]
        is_correct = btn.text()[2:].strip() == correct

        for b in self.buttons:
            b.setEnabled(False)
            if b.text()[2:].strip() == correct:
                b.setStyleSheet(
                    "font-size: 24px; padding: 12px; text-align: left;"
                    " background-color: #2d6a2d;"
                )
            elif b is btn and not is_correct:
                b.setStyleSheet(
                    "font-size: 24px; padding: 12px; text-align: left;"
                    " background-color: #8a2d2d;"
                )

        if is_correct:
            self.correct += 1
            self.feedback.setStyleSheet("font-size: 20px; color: #4caf50; padding: 8px;")
            self.feedback.setText("✅ Đúng!")
        else:
            self.feedback.setStyleSheet("font-size: 20px; color: #f44336; padding: 8px;")
            self.feedback.setText(f"❌ Sai. Đáp án: {correct}")

        self.index += 1
        QTimer.singleShot(1200, self._next_question)

    def _finish(self):
        self.storage.log_quiz("all", self.total, self.correct)
        pct = int(self.correct / self.total * 100) if self.total else 0
        self.q_label.setText(f"🎯 Hoàn thành!")
        self.feedback.setStyleSheet(
            f"font-size: 28px; padding: 16px; color: #4caf50;"
        )
        self.feedback.setText(f"{self.correct}/{self.total} đúng ({pct}%)")
        for b in self.buttons:
            b.setVisible(False)
        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("font-size: 24px; padding: 12px;")
        close_btn.clicked.connect(self.accept)
        self.btn_group.addWidget(close_btn)
