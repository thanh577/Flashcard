
import datetime
import logging

logger = logging.getLogger(__name__)


def calc_streak(review_log):
    days = sorted(set(r["reviewed_at"][:10] for r in review_log))
    streak = 0
    today = datetime.date.today()
    for offset in range(365):
        day = (today - datetime.timedelta(days=offset)).isoformat()
        if day in days:
            streak += 1
        else:
            break
    return streak


def calc_badges(stats_data):
    total_reviews = stats_data.get("total_reviews", 0)
    streak = stats_data.get("streak", 0)
    quiz_correct = stats_data.get("quiz_correct", 0)
    learned = stats_data.get("learned", 0)

    badges = []

    if total_reviews >= 1:
        badges.append(("🌟", "Lần đầu ôn tập", "Hoàn thành lượt ôn đầu tiên"))
    if total_reviews >= 10:
        badges.append(("📖", "10 Lượt ôn", "Hoàn thành 10 lượt ôn"))
    if total_reviews >= 100:
        badges.append(("📚", "100 Lượt ôn", "Hoàn thành 100 lượt ôn"))
    if total_reviews >= 500:
        badges.append(("🎓", "500 Lượt ôn", "Hoàn thành 500 lượt ôn"))

    if learned >= 10:
        badges.append(("🧠", "10 Thẻ", "Học 10 thẻ"))
    if learned >= 50:
        badges.append(("🧠", "50 Thẻ", "Học 50 thẻ"))
    if learned >= 100:
        badges.append(("🧠", "100 Thẻ", "Học 100 thẻ"))

    if streak >= 3:
        badges.append(("🔥", "3 Ngày liên tiếp", "Học 3 ngày liên tiếp"))
    if streak >= 7:
        badges.append(("🔥", "7 Ngày liên tiếp", "Học 7 ngày liên tiếp"))
    if streak >= 30:
        badges.append(("💪", "30 Ngày liên tiếp", "Học 30 ngày liên tiếp"))

    if quiz_correct >= 5:
        badges.append(("🎯", "Quiz 5 câu", "Đúng 5 câu trắc nghiệm"))
    if quiz_correct >= 20:
        badges.append(("🎯", "Quiz 20 câu", "Đúng 20 câu trắc nghiệm"))

    return badges


def calc_stats(cards, review_log, quiz_log):
    today = datetime.date.today().isoformat()
    today_reviews = sum(1 for r in review_log if r["reviewed_at"][:10] == today)
    total_reviews = len(review_log)
    learned = sum(1 for c in cards if c.get("next_review", "2000-01-01") > "2000-01-10")
    due_today = sum(1 for c in cards if c.get("next_review", "2000-01-01") <= today)
    streak = calc_streak(review_log)
    fav_count = sum(1 for c in cards if c.get("favorite"))

    quiz_total = sum(q["total"] for q in quiz_log)
    quiz_correct = sum(q["correct"] for q in quiz_log)

    by_quality = {}
    for r in review_log:
        q = r.get("quality", "unknown")
        by_quality[q] = by_quality.get(q, 0) + 1

    return {
        "total_cards": len(cards),
        "learned": learned,
        "due_today": due_today,
        "total_reviews": total_reviews,
        "today_reviews": today_reviews,
        "streak": streak,
        "favorites": fav_count,
        "quiz_total": quiz_total,
        "quiz_correct": quiz_correct,
        "by_quality": by_quality,
    }
