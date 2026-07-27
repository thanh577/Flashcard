
import os
import re
import json
import urllib.request
import urllib.error
from PyQt6.QtCore import QThread, pyqtSignal
from core.paths import user_data_dir

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
CACHE_FILENAME = "ai_explain_cache.json"


def _build_prompt(cmd):
    return (
        f"Bạn là chuyên gia Linux. Giải thích lệnh \"{cmd}\" bằng tiếng Việt.\n"
        f"Trả lời DUY NHẤT bằng JSON đúng khuôn mẫu sau, không thêm chữ nào khác, "
        f"không thêm ```markdown:\n"
        f'{{"desc": "mô tả ngắn gọn 1 câu", '
        f'"flags": {{"-x": "giải thích cờ -x bằng tiếng Việt"}}, '
        f'"examples": [["lệnh ví dụ đầy đủ", "mô tả ngắn", "kết quả giả lập hợp lý"]]}}\n'
        f"Chỉ liệt kê tối đa 5 cờ phổ biến nhất thực sự tồn tại của lệnh này. "
        f"Chỉ cho đúng 2 ví dụ. Nếu \"{cmd}\" KHÔNG phải lệnh Linux có thật, "
        f'trả về {{"desc": "", "flags": {{}}, "examples": []}}.'
    )


def _cache_path():
    return os.path.join(user_data_dir(), CACHE_FILENAME)


def load_cache():
    path = _cache_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    try:
        with open(_cache_path(), "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # cache là tiện ích thêm, lỗi ghi không nên làm gãy tính năng chính


class AILookupWorker(QThread):
    """Gọi Groq API ở luồng riêng để không làm đơ giao diện trong lúc chờ mạng."""
    finished_ok = pyqtSignal(str, dict)   # tên lệnh, info (desc/flags/examples)
    finished_err = pyqtSignal(str)        # thông báo lỗi hiển thị cho người dùng

    def __init__(self, cmd, api_key, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.api_key = api_key

    def run(self):
        try:
            payload = json.dumps({
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": _build_prompt(self.cmd)}],
                "max_tokens": 700,
                "temperature": 0.2,
            }).encode("utf-8")
            req = urllib.request.Request(
                GROQ_URL, data=payload, method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            text = data["choices"][0]["message"]["content"].strip()
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if not m:
                self.finished_err.emit("AI không trả về đúng định dạng mong đợi.")
                return
            obj = json.loads(m.group())
            desc = (obj.get("desc") or "").strip()
            if not desc:
                self.finished_err.emit(f"'{self.cmd}' có vẻ không phải lệnh Linux hợp lệ.")
                return

            examples = []
            for e in obj.get("examples", []):
                if isinstance(e, (list, tuple)) and len(e) == 3:
                    examples.append(tuple(e))

            info = {
                "desc": desc,
                "flags": obj.get("flags", {}) or {},
                "examples": examples,
            }
            self.finished_ok.emit(self.cmd, info)

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.finished_err.emit("API key không hợp lệ — kiểm tra lại trong Cài đặt.")
            else:
                self.finished_err.emit(f"Lỗi kết nối tới AI (HTTP {e.code}).")
        except urllib.error.URLError:
            self.finished_err.emit("Không kết nối được mạng — kiểm tra Internet rồi thử lại.")
        except json.JSONDecodeError:
            self.finished_err.emit("AI trả về dữ liệu không đọc được, thử lại giúp mình.")
        except Exception as e:
            self.finished_err.emit(f"Lỗi không xác định: {e}")
