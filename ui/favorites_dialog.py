
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QMessageBox)
from PyQt6.QtCore import Qt


class FavoritesDialog(QDialog):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("⭐ Yêu thích")
        self.resize(480, 400)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 20px;")
        layout.addWidget(QLabel("Danh sách thẻ yêu thích:"))
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_unfav = QPushButton("⭐ Bỏ yêu thích")
        btn_unfav.setStyleSheet("font-size: 18px; padding: 8px;")
        btn_unfav.clicked.connect(self._remove_fav)
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setStyleSheet("font-size: 18px; padding: 8px;")
        btn_refresh.clicked.connect(self._load)
        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet("font-size: 18px; padding: 8px;")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_unfav)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self._load()

    def _load(self):
        self.list_widget.clear()
        self.favs = self.storage.get_favorites()
        if not self.favs:
            self.list_widget.addItem("(Chưa có thẻ yêu thích nào)")
            return
        for c in self.favs:
            tag = {"english": "🇬🇧", "chinese": "🀄", "linux": "🐧"}.get(
                c.get("source", ""), ""
            )
            text = f"{tag} {c['front']}  →  {c['back']}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, c["id"])
            self.list_widget.addItem(item)

    def _remove_fav(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.information(self, "Chọn thẻ", "Hãy chọn một thẻ để bỏ yêu thích.")
            return
        cid = item.data(Qt.ItemDataRole.UserRole)
        self.storage.toggle_favorite(cid)
        self.storage.reload_cards()
        self._load()
