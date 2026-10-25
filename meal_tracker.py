import pandas as pd
from base_tracker import BaseTracker, ValidationError, MAX_CALORIES, whole_number, clean_text, clean_date
from storage import CSVStorage

class MealTracker(BaseTracker):
    COLUMNS = ['Date','Meal','Food','Calories']

    def add_meal(self, date, meal, food, calories):
        """Validate one meal, append it to the log, and save."""
        date = clean_date(date)
        meal = clean_text(meal, 'Meal') # Breakfast, Lunch, Dinner, Snack
        food = clean_text(food, 'Food') # Short description of what was eaten
        calories = whole_number(calories, 'Calories')
        if not 1 <= calories <= MAX_CALORIES:
            raise ValidationError(f"Calories must be between 1 and {MAX_CALORIES}")

        new_row = pd.DataFrame([{
            'Date': date,
            "Meal": meal,
            "Food": food,
            "Calories": calories,
        }])

        self.append_row(new_row)

    def add_from_row(self, row):
        self.add_meal(row["Date"], row["Meal"], row["Food"], row["Calories"])
        

if __name__ == "__main__":
    tracker = MealTracker(CSVStorage("data/test_meals.csv"))   # test file, not the real one

    tracker.add_meal("2026-10-20", "Breakfast", "Eggs and bread", 450)
    tracker.add_meal("2026-10-20", "Lunch", "Chicken and rice", 700)
    print(tracker.load())

    try:
        tracker.add_meal("2026-10-20", "Snack", "Dates", 'abc')   
    except ValidationError as e:
        print("Rejected:", e)
