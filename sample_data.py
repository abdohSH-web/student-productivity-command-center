import random
from datetime import date, timedelta

STUDY_SUBJECTS = {
    "Python": ["OOP", "Pandas groupby", "File I/O", "Error handling"],
    "English": ["Vocabulary", "Essay writing", "Listening practice"],
    "Graphic Design": ["Typography", "Color theory"],
    "University": ["Lecture review", "Assignment"],
}
ACTIVITIES = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Cardio"]
MAIN_MEALS = [
    ("Breakfast", "Eggs and bread", 350, 500),
    ("Lunch", "Chicken and rice", 600, 850),
    ("Dinner", "Tuna sandwich and salad", 450, 700),
]


def load_sample_data(study_tracker, workout_tracker, meal_tracker, days=21):
    """Fill the three trackers with `days` days of example entries.
    Meant for the public demo only: the app must never call this in CSV mode."""

    # A fixed seed makes the "random" numbers identical on every run,
    # so the demo always looks the same.
    rng = random.Random(42)
    today = date.today()

    for offset in range(days):
        day = today - timedelta(days=offset)     # today, yesterday, ...

        # 1-2 study sessions per day
        for _ in range(rng.randint(1, 2)):
            category = rng.choice(list(STUDY_SUBJECTS))
            study_tracker.add_session(
                day, category, rng.choice(STUDY_SUBJECTS[category]),
                rng.choice([30, 45, 60, 90]), rng.randint(2, 5), "Sample data",
            )

        # A workout on most days (skip two days out of every seven)
        if offset % 7 not in (2, 5):
            minutes = rng.choice([40, 45, 60, 75])
            workout_tracker.add_workout(
                day, rng.choice(ACTIVITIES), minutes, rng.randint(2, 5),
                notes="Sample data", calories_burned=minutes * rng.randint(5, 8),
            )

        # Three main meals every day
        for meal, food, low, high in MAIN_MEALS:
            meal_tracker.add_meal(day, meal, food, rng.randint(low, high))