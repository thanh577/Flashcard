
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
        interval = card.get("interval", 1)
        if quality == "again":
            interval = 1
        elif quality == "hard":
            interval = max(1, int(interval * 1.5))
        elif quality == "good":
            interval = max(1, int(interval * 2))
        elif quality == "easy":
            interval = max(1, int(interval * 3))

        card["interval"] = interval
        card["next_review"] = self._future(interval)

    def _future(self, days):
        return str(datetime.date.today() + datetime.timedelta(days=days))
