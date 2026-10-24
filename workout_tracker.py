import pandas as pd 
from base_tracker import BaseTracker, ValidationError, MAX_MINUTES, MAX_CALORIES, whole_number, clean_text, clean_date
from storage import CSVStorage

class WorkoutTracker(BaseTracker):
    COLUMNS = ['Date','Activity','Time','Intensity', 'Calories_burned', 'Notes']

    def add_workout(self, date, activity, minutes, intensity, calories_burned=0, notes=""):
        """Validate one workout, add it to the log, and save."""
        # 1# Validate everything first. The file isn't touched yet.
        date = clean_date(date)
        activity = clean_text(activity, 'Activity')
        minutes = whole_number(minutes, 'Minutes')
        if not 1 <= minutes <= MAX_MINUTES:
            raise ValidationError(f"Minutes must be between 1 and {MAX_MINUTES}")
        intensity = whole_number(intensity, "Intensity")
        if not 1 <= intensity <= 5:
            raise ValidationError("Intensity must be between 1 and 5")
        calories_burned = whole_number(calories_burned, 'Calories_burned')
        if not 0 <= calories_burned <= MAX_CALORIES:
            raise ValidationError(f"Calories_burned must be between 0 and {MAX_CALORIES}")
        notes = "" if notes is None else str(notes).strip()

        # 2# Build the new row (a one-row DataFarme).
        new_row = pd.DataFrame([{
            "Date": date,
            'Activity': activity,
            'Time': minutes,
            "Intensity": intensity,
            "Calories_burned": calories_burned,
            "Notes": notes,
        }])

        self.append_row(new_row)

if __name__ == "__main__":
    tracker = WorkoutTracker(CSVStorage("./data/test_workout.csv"))   # test file, not the real one

    tracker.add_workout("2026-10-20", "Chest", 60, 4, 800, "Bench press day")
    print(tracker.load())

    try:
        tracker.add_workout("2026-10-20", "Legs", 45, 9)   # intensity 9 -> rejected
    except ValidationError as e:
        print("Rejected:", e)

