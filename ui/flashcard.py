
import re
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton,
                             QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt
from ui.explain_dialog import CMDS
from core.theme import GREEN, RED, ACCENT, FG2, GOLD, BG_CORRECT, BG_WRONG


class FlashCard(QWidget):
    def __init__(self, speak_callback=None, fav_callback=None, answer_callback=None):
        super().__init__()
        self.setObjectName("FlashCard")
        self.speak_callback = speak_callback
        self.fav_callback = fav_callback
        self.answer_callback = answer_callback
        self.front = True
        self.data = None
        self.answered = False

        self.label = QLabel("...")
        self.label.setObjectName("card_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.mousePressEvent = lambda e: self.flip()

        self.btn_speak = QPushButton("🔊 Nghe")
        self.btn_speak.setObjectName("btn_speak")
        self.btn_speak.clicked.connect(self._on_speak)

        self.btn_fav = QPushButton("☆")
        self.btn_fav.setObjectName("btn_fav")
        self.btn_fav.clicked.connect(self._on_fav)

        self.practice_widget = QWidget()
        pw = QVBoxLayout(self.practice_widget)
        pw.setContentsMargins(20, 10, 20, 10)

        self.practice_prompt = QLabel()
        self.practice_prompt.setObjectName("practice_prompt")
        pw.addWidget(self.practice_prompt)

        self.practice_input = QLineEdit()
        self.practice_input.setObjectName("practice_input")
        self.practice_input.returnPressed.connect(self._check_practice)
        pw.addWidget(self.practice_input)

        prac_btn_row = QHBoxLayout()
        self.btn_check = QPushButton("✅ Kiểm tra")
        self.btn_check.setObjectName("btn_check")
        self.btn_check.clicked.connect(self._check_practice)
        prac_btn_row.addWidget(self.btn_check)

        self.btn_skip = QPushButton("⏭ Bỏ qua")
        self.btn_skip.setObjectName("btn_skip")
        self.btn_skip.clicked.connect(self._skip_practice)
        prac_btn_row.addWidget(self.btn_skip)

        self.btn_next = QPushButton("Tiếp →")
        self.btn_next.setObjectName("btn_next")
        self.btn_next.setVisible(False)
        self.btn_next.clicked.connect(self._next_card)
        prac_btn_row.addWidget(self.btn_next)

        pw.addLayout(prac_btn_row)

        self.practice_feedback = QLabel()
        self.practice_feedback.setObjectName("practice_feedback")
        self.practice_feedback.setWordWrap(True)
        self.practice_feedback.setVisible(False)
        pw.addWidget(self.practice_feedback)

        self.btn_linux_next = QPushButton("▶ Lệnh tiếp theo")
        self.btn_linux_next.setObjectName("btn_linux_next")
        self.btn_linux_next.setVisible(False)
        self.btn_linux_next.clicked.connect(self._next_card)

        top_row = QHBoxLayout()
        top_row.addWidget(self.btn_fav)
        top_row.addStretch()
        top_row.addWidget(self.btn_speak)
        top_row.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addWidget(self.label)
        layout.addWidget(self.practice_widget)
        layout.addWidget(self.btn_linux_next)
        layout.addStretch()
        self.setLayout(layout)

    def set_data(self, data):
        self.data = data
        self.answered = False
        self._update_fav_btn()
        self._show_front()

    def _update_fav_btn(self):
        if self.data and self.data.get("favorite"):
            self.btn_fav.setText("⭐")
            self.btn_fav.setStyleSheet(f"color: {GOLD};")
        else:
            self.btn_fav.setText("☆")
            self.btn_fav.setStyleSheet(f"color: {FG2};")

    def _show_front(self):
        self.front = True
        data = self.data or {}
        src = data.get("source", "")
        front_text = data.get("front", "?")
        has_practice = src in ("english", "chinese")

        self.practice_widget.setVisible(has_practice)
        if has_practice:
            self.practice_input.setEnabled(True)
            self.practice_input.clear()
            self.practice_input.setFocus()
            self.btn_check.setVisible(True)
            self.btn_skip.setVisible(True)
            self.practice_feedback.setVisible(False)
            self.btn_next.setVisible(False)
            self.practice_input.setStyleSheet("")

        self.btn_linux_next.setVisible(src == "linux")

        tag = {"english": "🇬🇧", "chinese": "🀄", "linux": "🐧"}.get(src, "")
        if has_practice:
            self.practice_prompt.setText(f"{tag} Gõ nghĩa tiếng Việt (nghe rồi gõ):")

        src_vi = {"english": "Tiếng Anh", "chinese": "Tiếng Trung", "linux": "Linux"}.get(src, src)
        self.label.setText(
            f"<div style='text-align:center;'>"
            f"<span style='color:#888;font-size:40px;'>{tag} {src_vi}</span>"
            f"<br><br><b style='font-size:144px;'>{front_text}</b>"
            f"<br><br><span style='color:#aaa;font-size:40px;'>— nhấn để lật —</span>"
            f"</div>"
        )
        self.label.setStyleSheet("")

    def _format_back(self, data):
        front = data.get("front", "")
        back = data.get("back", "")
        example = data.get("example", "")
        source = data.get("source", "")
        lines = back.replace("\n", "<br>")
        if source == "chinese":
            pinyin = data.get("pinyin", "")
            return (
                f"<div style='text-align:center;'>"
                f"<b style='font-size:96px; color:#cc3333;'>{front}</b>"
                f"<br><i style='font-size:62px; color:#666;'>{pinyin}</i>"
                f"<br><br><span style='font-size:62px;'>{lines}</span>"
                + (f"<br><br><span style='color:#555;font-size:50px;'><i>{example}</i></span>" if example else "")
                + f"<br><br><span style='color:#aaa;font-size:40px;'>— nhấn để về —</span>"
                + f"</div>"
            )
        if source == "linux":
            options_raw = data.get("options", "")
            options_html = ""
            if options_raw and options_raw != "(không có option phổ biến)":
                opts = [o.strip() for o in options_raw.split(";;") if o.strip()]
                if opts:
                    options_html = (
                        "<br><br><span style='font-size:40px; color:#ffa726;'>▸ Các cờ:</span>"
                        + "".join(
                            f"<br><span style='font-size:36px; color:#ccc;'>  {o}</span>"
                            for o in opts
                        )
                    )

            cmd_info = CMDS.get(front)
            examples_html = ""
            if cmd_info and cmd_info.get("examples"):
                examples_html = "<br><br><span style='font-size:40px; color:#ffa726;'>▸ Ví dụ:</span>"
                for cmd_ex, desc, output in cmd_info["examples"][:2]:
                    examples_html += f"<br><span style='font-size:32px; color:#aaa;'>$ {cmd_ex}</span>"

            return (
                f"<div style='text-align:center;'>"
                f"<b style='font-size:96px; color:#3366cc;'>{front}</b>"
                f"<br><br><span style='font-size:62px;'>{lines}</span>"
                + options_html
                + examples_html
                + f"<br><br><span style='color:#aaa;font-size:40px;'>— nhấn để về —</span>"
                + f"</div>"
            )
        return (
            f"<div style='text-align:center;'>"
            f"<b style='font-size:96px; color:#2d8a2d;'>{front}</b>"
            f"<br><br><span style='font-size:76px;'>{lines}</span>"
            + (f"<br><br><span style='color:#555;font-size:50px;'><i>{example}</i></span>" if example else "")
            + f"<br><br><span style='color:#aaa;font-size:40px;'>— nhấn để về —</span>"
            + f"</div>"
        )

    def flip(self):
        if not self.data:
            return
        if self.front:
            self.front = False
            self.label.setText(self._format_back(self.data))
            self.practice_widget.setVisible(False)
        else:
            self._show_front()

    def _get_answer(self):
        return self.data["back"].lower()

    def _check_practice(self):
        if self.answered:
            return
        self.answered = True
        correct = self._get_answer()
        user = self.practice_input.text().strip().lower()
        is_correct = self._normalize(user) == self._normalize(correct)

        if is_correct:
            self.practice_feedback.setStyleSheet(f"color: {GREEN};")
            self.practice_feedback.setText(f"✅ Đúng!")
            self.practice_input.setStyleSheet(f"background-color: {BG_CORRECT};")
            if self.answer_callback:
                self.answer_callback("good")
        else:
            self.practice_feedback.setStyleSheet(f"color: {RED};")
            self.practice_feedback.setText(f"❌ Sai. Đáp án: {self.data['back']}")
            self.practice_input.setStyleSheet(f"background-color: {BG_WRONG};")
            if self.answer_callback:
                self.answer_callback("again")

        self.practice_feedback.setVisible(True)
        self.practice_input.setEnabled(False)
        self.btn_check.setVisible(False)
        self.btn_skip.setVisible(False)
        self.btn_next.setVisible(True)
        self.btn_next.setFocus()

    def _skip_practice(self):
        if self.answered:
            return
        self.answered = True
        self.practice_feedback.setStyleSheet(f"color: {ACCENT};")
        self.practice_feedback.setText(f"⏭ Đáp án: {self.data['back']}")
        self.practice_feedback.setVisible(True)
        self.practice_input.setEnabled(False)
        self.btn_check.setVisible(False)
        self.btn_skip.setVisible(False)
        self.btn_next.setVisible(True)
        self.btn_next.setFocus()
        if self.answer_callback:
            self.answer_callback("again")

    def _next_card(self):
        if self.answer_callback:
            self.answer_callback("_next")

    def _on_speak(self):
        if self.speak_callback and self.data:
            self.speak_callback(self.data)

    def _on_fav(self):
        if self.fav_callback and self.data:
            self.fav_callback(self.data)
            self._update_fav_btn()

    @staticmethod
    def _normalize(s):
        s = s.strip().lower()
        s = re.sub(r'\s+', ' ', s)
        s = s.replace('/', ' / ')
        s = re.sub(r'\s+', ' ', s).strip()
        return s
