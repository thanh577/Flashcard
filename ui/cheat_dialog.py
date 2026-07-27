
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from ui.explain_dialog import CMDS


class CheatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Tra nhanh Linux")
        self.resize(600, 500)

        layout = QVBoxLayout()

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("gõ tên lệnh (vd: grep)")
        self.input_box.setStyleSheet("font-size: 22px; padding: 8px;")
        self.input_box.returnPressed.connect(self._search)
        input_row.addWidget(self.input_box)

        btn_search = QPushButton("🔍 Tìm")
        btn_search.setStyleSheet("font-size: 18px; padding: 8px;")
        btn_search.clicked.connect(self._search)
        input_row.addWidget(btn_search)
        layout.addLayout(input_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.result_widget)
        layout.addWidget(scroll)

        quick_row = QHBoxLayout()
        for name in sorted(CMDS.keys())[:8]:
            btn = QPushButton(name)
            btn.setStyleSheet("font-size: 14px; padding: 4px 8px;")
            btn.clicked.connect(lambda checked, n=name: self._show_cheat(n))
            quick_row.addWidget(btn)
        quick_row.addStretch()
        layout.addLayout(quick_row)

        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("font-size: 18px; padding: 8px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def _search(self):
        cmd = self.input_box.text().strip().lower()
        if not cmd:
            return
        if cmd in CMDS:
            self._show_cheat(cmd)
            return
        matches = [k for k in CMDS if k.startswith(cmd)]
        if matches:
            self._show_cheat(matches[0])
        else:
            self._show_not_found(cmd)

    def _clear(self):
        for i in reversed(range(self.result_layout.count())):
            w = self.result_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

    def _add_line(self, text, style=""):
        lbl = QLabel(text)
        base = "font-size: 17px; padding: 2px 0;"
        lbl.setStyleSheet(base + style)
        lbl.setWordWrap(True)
        self.result_layout.addWidget(lbl)

    def _add_card(self, title, items, emoji):
        if not items:
            return
        self._add_line("")
        self._add_line(f"{emoji}  {title}", "font-size: 19px; font-weight: bold; color: #ffa726;")
        for line in items:
            self._add_line(f"    {line}")

    def _show_cheat(self, cmd):
        self._clear()
        self.input_box.setText(cmd)
        info = CMDS[cmd]

        self._add_line(f"📋 {cmd}", "font-size: 24px; font-weight: bold; color: #4caf50;")
        self._add_line(f"{info['desc']}", "font-size: 18px; color: #42a5f5; padding-bottom: 6px;")
        self._add_line("─" * 50)

        self._add_card("Các cờ (flags)", [f"{f}  →  {d}" for f, d in sorted(info.get("flags", {}).items())], "📘")

        examples = info.get("examples", [])
        if examples:
            self._add_line("")
            self._add_line("📝  Ví dụ:", "font-size: 19px; font-weight: bold; color: #ffa726;")
            for cmd_ex, desc, output in examples:
                card = QWidget()
                card.setStyleSheet(
                    "background-color: #1e1e2e; border: 1px solid #3a3a5a;"
                    " border-radius: 8px; padding: 10px; margin: 4px 0;"
                )
                cl = QVBoxLayout(card)
                cl.setContentsMargins(10, 6, 10, 6)

                d = QLabel(desc)
                d.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffa726;")
                d.setWordWrap(True)
                cl.addWidget(d)

                c = QLabel(f"$ {cmd_ex}")
                c.setStyleSheet("font-size: 15px; color: #80cbc4; font-family: monospace;")
                c.setWordWrap(True)
                cl.addWidget(c)

                if output:
                    o = QLabel(output)
                    o.setStyleSheet("font-size: 14px; color: #aaa; font-family: monospace;")
                    o.setWordWrap(True)
                    cl.addWidget(o)

                self.result_layout.addWidget(card)

        self._add_line("")

    def _show_not_found(self, cmd):
        self._clear()
        self._add_line(f"Không có thông tin cho '{cmd}'.")
        self._add_line("")
        self._add_line("Các lệnh có sẵn: " + ", ".join(sorted(CMDS.keys())))
