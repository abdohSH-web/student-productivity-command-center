from pathlib import Path
import pandas as pd
from base_tracker import BaseTracker, ValidationError, MAX_MINUTES, whole_number, clean_text, clean_date




class StorageError(Exception):
    """Raised when the CSV file can't be read/written or has a wrong structure"""

class ValidationError(Exception):
    """Raised when the data the user entered is not valid"""


class StudyTracker(BaseTracker):
    COLUMNS = ['Date','Category','Subject','Time','Understanding','Notes']

    def add_session(self, date, category, subject, minutes, understanding, notes=''):
        """Validate one studying session, append it to the log, and save"""

        # 1) Validate everything:
        # Date: Must be convertible to a real date
        # The function clean_date() from base_tracker validate it
        date = clean_date(date)
        # Textfileds: strip spaces and don't allow empty values
        category = clean_text(category, "Category")
        subject = clean_text(subject, "Subject")
         # reject subjects made only of digits
        if subject.isdigit():
            raise ValidationError("Subject can't be only numbers. Describe what you studied.")
        # Minutes: Must be a whole number between 1 and MAX_MINUTES
        minutes = whole_number(minutes, "Minutes")
        if not 1 <= minutes <= MAX_MINUTES:
            raise ValidationError(f"Minutes must be between 1 and {MAX_MINUTES}")
        #Understanding: Must be a number between 1 and 5
        understanding = whole_number(understanding, "Understanding")
        if not 1 <= understanding <= 5:
            raise ValidationError("Understanding must be between 1 and 5")
        notes = str(notes).strip()

        # 2) build the new row (a one_row DataFrame)
        new_row = pd.DataFrame([{
            'Date': date,
            'Category': category,
            "Subject": subject,
            "Time": minutes,
            "Understanding": understanding,
            "Notes": notes,
        }])

        # 3) append to the existing log and save

        self.append_row(new_row)

    def add_from_row(self, row):
        self.add_session(
            row["Date"], row["Category"], row["Subject"],
            row["Time"], row["Understanding"], row["Notes"],
        )
        

if __name__ == "__main__":
    tracker = StudyTracker("data/test_log.csv")   # test file, not the real one

    # A valid session
    tracker.add_session("2026-10-12", "Python", "I/O", '60.0', 4, "good session")
    print(tracker.load())

    # An invalid session: our ValidationError should catch it
    try:
        tracker.add_session("2026-10-12", "Python", "OOP", -5, 4)
    except ValidationError as e:
        print("Rejected:", e)

    
        