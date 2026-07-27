
import datetime
import random
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, storage):
        self.storage = storage

    @property
    def cards(self):
        return self.storage.cards

    def get_next_card(self):
        today = datetime.date.today()
        due = []
        for c in self.cards:
            try:
                nr = datetime.date.fromisoformat(c["next_review"])
            except (ValueError, KeyError) as e:
                logger.warning("Invalid next_review %s for card %s: %s",
                               c.get("next_review"), c.get("front"), e)
                continue
            if nr <= today:
                due.append(c)

        if due:
            return random.choice(due)
        if self.cards:
            return random.choice(self.cards)
        return None

    def review(self, quality, card):
        """Thuật toán SM-2 (nền tảng của Anki) — mỗi thẻ có "độ dễ" (ease
        factor) RIÊNG, tự thích ứng theo lịch sử trả lời của chính thẻ đó,
        thay vì nhân interval theo 1 công thức cứng chung cho mọi thẻ.

        Ánh xạ 4 mức trả lời của app sang thang điểm 0-5 gốc của SM-2:
            again → 0 (quên hẳn)   hard → 3   good → 4   easy → 5 (hoàn hảo)
        """
        q = {"again": 0, "hard": 3, "good": 4, "easy": 5}.get(quality, 4)

        ef = card.get("ease_factor", 2.5)
        reps = card.get("repetitions", 0)
        interval = card.get("interval", 1)

        if q < 3:
            # Trả lời sai/quên — về lại bước học đầu tiên (interval=1),
            # không được tính là 1 lần lặp lại thành công
            reps = 0
            interval = 1
        else:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = max(1, round(interval * ef))
            reps += 1

        # Cập nhật ease factor theo đúng công thức gốc SM-2 — luôn cập nhật
        # (kể cả khi trả lời sai) để phản ánh đúng độ khó thực tế của thẻ,
        # không bao giờ để dưới 1.3 (mức sàn tối thiểu theo thuật toán gốc)
        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        ef = max(1.3, ef)

        card["ease_factor"] = round(ef, 2)
        card["repetitions"] = reps
        card["interval"] = interval
        card["next_review"] = self._future(interval)

    def _future(self, days):
        return str(datetime.date.today() + datetime.timedelta(days=days))
