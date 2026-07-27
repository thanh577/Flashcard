
import sqlite3
import json
import os
import shutil
import glob
import datetime
import logging
from core.paths import resource_path, user_data_dir

logger = logging.getLogger(__name__)

DB_FILENAME = "flashcard.db"
BACKUP_KEEP = 5  # chỉ giữ lại 5 bản sao lưu gần nhất, tránh tích tụ vô hạn

class Storage:
    def __init__(self):
        data_dir = user_data_dir()
        self._db_path = os.path.join(data_dir, DB_FILENAME)
        self._config_path = os.path.join(data_dir, "config.json")

        self._init_db()
        self._backup_db()
        self._seed_from_json()

        self.config = self._load_config()
        self.cards = self._load_cards()

    def _backup_db(self):
        """Sao lưu flashcard.db mỗi lần mở app — nếu DB bị lỗi/hỏng ở phiên
        sau, vẫn còn bản backup gần nhất để khôi phục thủ công (đổi tên file
        backup thành flashcard.db). Tự động chỉ giữ BACKUP_KEEP bản gần nhất,
        không tích tụ vô hạn theo thời gian."""
        if not os.path.exists(self._db_path):
            return  # máy mới, chưa có gì để sao lưu
        try:
            backup_dir = os.path.join(os.path.dirname(self._db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"flashcard_{ts}.db")
            shutil.copy2(self._db_path, backup_path)

            existing = sorted(glob.glob(os.path.join(backup_dir, "flashcard_*.db")))
            for old in existing[:-BACKUP_KEEP]:
                try:
                    os.remove(old)
                except Exception:
                    pass
        except Exception as e:
            logger.warning("Sao lưu DB thất bại (không ảnh hưởng hoạt động chính): %s", e)

    def _conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        conn = self._conn()
        try:
            try:
                conn.execute("ALTER TABLE cards ADD COLUMN options TEXT DEFAULT ''")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE cards ADD COLUMN ease_factor REAL DEFAULT 2.5")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE cards ADD COLUMN repetitions INTEGER DEFAULT 0")
            except Exception:
                pass

            conn.executescript("""
                CREATE TABLE IF NOT EXISTS cards (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    front       TEXT NOT NULL,
                    back        TEXT NOT NULL,
                    source      TEXT NOT NULL DEFAULT '',
                    pinyin      TEXT DEFAULT '',
                    example     TEXT DEFAULT '',
                    pronunciation TEXT DEFAULT '',
                    example_pronunciation TEXT DEFAULT '',
                    options     TEXT DEFAULT '',
                    interval    INTEGER DEFAULT 1,
                    ease_factor REAL DEFAULT 2.5,
                    repetitions INTEGER DEFAULT 0,
                    next_review TEXT DEFAULT '2000-01-01',
                    favorite    INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS review_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id     INTEGER NOT NULL,
                    quality     TEXT NOT NULL,
                    source      TEXT DEFAULT '',
                    reviewed_at TEXT DEFAULT (datetime('now','localtime'))
                );
                CREATE TABLE IF NOT EXISTS config (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS quiz_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    source      TEXT DEFAULT '',
                    total       INTEGER DEFAULT 0,
                    correct     INTEGER DEFAULT 0,
                    quizzed_at  TEXT DEFAULT (datetime('now','localtime'))
                );
            """)
            conn.commit()
        except Exception as e:
            logger.error("Init DB failed: %s", e)
            raise
        finally:
            conn.close()

    def _seed_from_json(self):
        conn = self._conn()
        try:
            count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        except Exception as e:
            logger.error("Check card count failed: %s", e)
            conn.close()
            return
        if count > 0:
            conn.close()
            return

        src_map = {
            "english": "english.json",
            "chinese": "chinese.json",
            "linux":   "linux.json",
        }
        for key, filename in src_map.items():
            path = resource_path("data", filename)
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
            except Exception as e:
                logger.warning("Skip %s (cannot read): %s", filename, e)
                continue
            for item in items:
                try:
                    conn.execute(
                        """INSERT INTO cards
                           (front, back, source, pinyin, example,
                            pronunciation, example_pronunciation,
                            options, interval, next_review)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (
                            item.get("front", ""),
                            item.get("back", ""),
                            item.get("source", key),
                            item.get("pinyin", ""),
                            item.get("example", ""),
                            item.get("pronunciation", ""),
                            item.get("example_pronunciation", ""),
                            item.get("options", ""),
                            item.get("interval", 1),
                            item.get("next_review", "2000-01-01"),
                        ),
                    )
                except Exception as e:
                    logger.error("Insert card %s from %s failed: %s",
                                 item.get("front"), filename, e)
            conn.commit()
        conn.close()

    def _load_config(self):
        default = {
            "enabled_sources": ["english", "chinese", "linux"],
            "audio_enabled": True,
            "auto_start": False,
            "default_interval": 1,
            "desktop_widget_enabled": True,
            "widget_interval_minutes": 5,
            "widget_pos": None,
            "widget_size": None,
            "widget_transparency": 35,     # 0 = gần như đục hoàn toàn, 90 = rất trong suốt
            "widget_always_on_top": True,
            "groq_api_key": "",
        }
        if not os.path.exists(self._config_path):
            return default
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            default.update(data)
        except Exception as e:
            logger.error("Load config failed: %s", e)
        return default

    def save_config(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Save config failed: %s", e)

    def _load_cards(self):
        enabled = self.config.get("enabled_sources", ["english", "chinese", "linux"])
        if not enabled:
            return [self._empty_card()]

        conn = self._conn()
        try:
            placeholders = ",".join("?" for _ in enabled)
            rows = conn.execute(
                f"SELECT * FROM cards WHERE source IN ({placeholders}) ORDER BY id",
                enabled,
            ).fetchall()
        except Exception as e:
            logger.error("Load cards failed: %s", e)
            return [self._empty_card()]
        finally:
            conn.close()

        cards = []
        for row in rows:
            cards.append({
                "id": row["id"],
                "front": row["front"],
                "back": row["back"],
                "source": row["source"],
                "pinyin": row["pinyin"] or "",
                "example": row["example"] or "",
                "pronunciation": row["pronunciation"] or "",
                "example_pronunciation": row["example_pronunciation"] or "",
                "options": row["options"] or "",
                "interval": row["interval"],
                "ease_factor": row["ease_factor"] if row["ease_factor"] is not None else 2.5,
                "repetitions": row["repetitions"] or 0,
                "next_review": row["next_review"],
                "favorite": row["favorite"] or 0,
            })
        if not cards:
            cards.append(self._empty_card())
        return cards

    @staticmethod
    def _empty_card():
        return {
            "id": -1,
            "front": "Không có dữ liệu",
            "back": "Bật ít nhất một nguồn trong Cài đặt.",
            "source": "none",
            "options": "",
            "interval": 1,
            "ease_factor": 2.5,
            "repetitions": 0,
            "next_review": "2000-01-01",
            "favorite": 0,
        }

    def save(self):
        conn = self._conn()
        try:
            for card in self.cards:
                cid = card.get("id", -1)
                if cid < 0:
                    continue
                conn.execute(
                    "UPDATE cards SET interval=?, ease_factor=?, repetitions=?, "
                    "next_review=?, favorite=? WHERE id=?",
                    (card["interval"], card.get("ease_factor", 2.5), card.get("repetitions", 0),
                     card["next_review"], card.get("favorite", 0), cid),
                )
            conn.commit()
        except Exception as e:
            logger.error("Save progress failed: %s", e)
        finally:
            conn.close()

    def reload_cards(self):
        self.cards = self._load_cards()

    def get_all_cards(self):
        conn = self._conn()
        try:
            rows = conn.execute("SELECT * FROM cards ORDER BY source, id").fetchall()
            cards = []
            for row in rows:
                cards.append({
                    "id": row["id"],
                    "front": row["front"],
                    "back": row["back"],
                    "source": row["source"],
                    "pinyin": row["pinyin"] or "",
                    "example": row["example"] or "",
                    "pronunciation": row["pronunciation"] or "",
                    "example_pronunciation": row["example_pronunciation"] or "",
                    "options": row["options"] or "",
                    "interval": row["interval"],
                    "next_review": row["next_review"],
                    "favorite": row["favorite"] or 0,
                })
            return cards
        except Exception as e:
            logger.error("Get all cards failed: %s", e)
            return []
        finally:
            conn.close()

    def add_card(self, front, back, source, example="", pinyin="", options="",
                 pronunciation="", example_pronunciation=""):
        conn = self._conn()
        try:
            cur = conn.execute(
                "INSERT INTO cards (front, back, source, pinyin, example, options, "
                "pronunciation, example_pronunciation) VALUES (?,?,?,?,?,?,?,?)",
                (front, back, source, pinyin, example, options,
                 pronunciation, example_pronunciation),
            )
            conn.commit()
            new_id = cur.lastrowid
            logger.info("Added card id=%s front=%s source=%s", new_id, front, source)
            return new_id
        except Exception as e:
            logger.error("Add card failed front=%s: %s", front, e)
            return None
        finally:
            conn.close()

    def toggle_favorite(self, card_id):
        conn = self._conn()
        try:
            cur = conn.execute("SELECT favorite FROM cards WHERE id=?", (card_id,))
            row = cur.fetchone()
            if row is None:
                return None
            new_val = 0 if row["favorite"] else 1
            conn.execute("UPDATE cards SET favorite=? WHERE id=?", (new_val, card_id))
            conn.commit()
            return bool(new_val)
        except Exception as e:
            logger.error("Toggle favorite failed id=%s: %s", card_id, e)
            return None
        finally:
            conn.close()

    def get_favorites(self):
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM cards WHERE favorite=1 ORDER BY source, front"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Get favorites failed: %s", e)
            return []
        finally:
            conn.close()

    def log_review(self, card_id, quality, source=""):
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO review_log (card_id, quality, source) VALUES (?,?,?)",
                (card_id, quality, source),
            )
            conn.commit()
        except Exception as e:
            logger.error("Log review failed: %s", e)
        finally:
            conn.close()

    def log_quiz(self, source, total, correct):
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO quiz_log (source, total, correct) VALUES (?,?,?)",
                (source, total, correct),
            )
            conn.commit()
        except Exception as e:
            logger.error("Log quiz failed: %s", e)
        finally:
            conn.close()

    def get_review_log(self, days=30):
        conn = self._conn()
        try:
            rows = conn.execute(
                """SELECT * FROM review_log
                   WHERE reviewed_at >= datetime('now','-%d days','localtime')
                   ORDER BY reviewed_at DESC""" % days,
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Get review log failed: %s", e)
            return []
        finally:
            conn.close()

    def get_quiz_log(self, days=30):
        conn = self._conn()
        try:
            rows = conn.execute(
                """SELECT * FROM quiz_log
                   WHERE quizzed_at >= datetime('now','-%d days','localtime')
                   ORDER BY quizzed_at DESC""" % days,
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Get quiz log failed: %s", e)
            return []
        finally:
            conn.close()
