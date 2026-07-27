
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QWidget, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from core.stats import calc_stats, calc_badges, calc_streak


class StatsDialog(QDialog):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("📊 Thống kê & Lịch sử")
        self.resize(520, 450)

        review_log = storage.get_review_log(365)
        quiz_log = storage.get_quiz_log(365)
        self.stats = calc_stats(storage.cards, review_log, quiz_log)
        self.stats["streak"] = calc_streak(review_log)
        self.badges = calc_badges(self.stats)

        tabs = QTabWidget()
        tabs.addTab(self._build_overview(), "📊 Tổng quan")
        tabs.addTab(self._build_badges(), "🏆 Huy hiệu")
        tabs.addTab(self._build_history(review_log), "📜 Lịch sử")
        tabs.addTab(self._build_quiz_history(quiz_log), "🎯 Trắc nghiệm")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("font-size: 18px; padding: 8px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

    def _section(self, title):
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 22px; font-weight: bold; padding: 8px 0;")
        return lbl

    def _row(self, left, right):
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(8, 2, 8, 2)
        l = QLabel(left)
        l.setStyleSheet("font-size: 18px;")
        r = QLabel(str(right))
        r.setStyleSheet("font-size: 18px; font-weight: bold; color: #4caf50;")
        h.addWidget(l)
        h.addStretch()
        h.addWidget(r)
        return w

    def _build_overview(self):
        w = QWidget()
        l = QVBoxLayout(w)
        s = self.stats
        l.addWidget(self._section("📊 Tổng quan học tập"))
        l.addWidget(self._row("Tổng số thẻ:", s["total_cards"]))
        l.addWidget(self._row("Đã học:", s["learned"]))
        l.addWidget(self._row("Cần ôn hôm nay:", s["due_today"]))
        l.addWidget(self._row("Yêu thích:", s["favorites"]))
        l.addWidget(self._section("📅 Hoạt động"))
        l.addWidget(self._row("Tổng lượt ôn:", s["total_reviews"]))
        l.addWidget(self._row("Hôm nay:", s["today_reviews"]))
        l.addWidget(self._row("Chuỗi:", f"{s['streak']} ngày"))
        l.addWidget(self._section("🎯 Trắc nghiệm"))
        l.addWidget(self._row("Câu đã làm:", s["quiz_total"]))
        l.addWidget(self._row("Đúng:", s["quiz_correct"]))
        if s.get("by_quality"):
            l.addWidget(self._section("📈 Chất lượng trả lời"))
            for q, n in sorted(s["by_quality"].items()):
                l.addWidget(self._row(f"  {q}:", n))
        l.addStretch()
        return w

    def _build_badges(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(self._section(f"🏆 Huy hiệu ({len(self.badges)})"))
        if not self.badges:
            l.addWidget(QLabel("Chưa có huy hiệu nào. Hãy học để mở khóa!"))
        for emoji, name, desc in self.badges:
            card = QWidget()
            card.setStyleSheet(
                "background-color: #2a2a3a; border-radius: 8px; padding: 8px; margin: 4px;"
            )
            h = QHBoxLayout(card)
            h.addWidget(QLabel(f"{emoji}  {name}"))
            h.addStretch()
            d = QLabel(desc)
            d.setStyleSheet("color: #aaa; font-size: 14px;")
            h.addWidget(d)
            l.addWidget(card)
        l.addStretch()
        return w

    def _build_history(self, review_log):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(self._section(f"📜 Lịch sử ({len(review_log)} lượt)"))

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Thời gian", "Thẻ", "Kết quả"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        max_rows = min(len(review_log), 500)
        table.setRowCount(max_rows)
        for i, r in enumerate(review_log[:max_rows]):
            table.setItem(i, 0, QTableWidgetItem(r["reviewed_at"][:16]))
            table.setItem(i, 1, QTableWidgetItem(f"id={r['card_id']}"))
            table.setItem(i, 2, QTableWidgetItem(r["quality"]))
        table.resizeColumnsToContents()
        l.addWidget(table)
        return w

    def _build_quiz_history(self, quiz_log):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(self._section(f"🎯 Lịch sử trắc nghiệm ({len(quiz_log)} lần)"))

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Thời gian", "Nguồn", "Đúng/Tổng", "%"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        table.setRowCount(len(quiz_log))
        for i, q in enumerate(quiz_log):
            table.setItem(i, 0, QTableWidgetItem(q["quizzed_at"][:16]))
            table.setItem(i, 1, QTableWidgetItem(q["source"]))
            table.setItem(i, 2, QTableWidgetItem(f"{q['correct']}/{q['total']}"))
            pct = int(q["correct"] / q["total"] * 100) if q["total"] else 0
            table.setItem(i, 3, QTableWidgetItem(f"{pct}%"))
        table.resizeColumnsToContents()
        l.addWidget(table)
        return w
