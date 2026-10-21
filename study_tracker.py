from pathlib import Path
import pandas as pd
from base_tracker import BaseTracker, ValidationError, MAX_MINUTES, whole_number, clean_text, clean_date


COLUMNS = ['Date','Category','Subject','Time','Understanding','Notes']

class StorageError(Exception):
    """Raised when the CSV file can't be read/written or has a wrong structure"""

class ValidationError(Exception):
    """Raised when the data the user entered is not valid"""

def _whole_number(value, field_name):
    """Convert value to an int, but REJECT decimals instead of silently cutting them."""
    try:
        # float() accepts "60", "60.7", 60, 60.7 ... and fails on text like "abc"
        number = float(value)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"{field_name} must be a number, got {value!r}") from e

    # 60.0 is fine (it IS a whole number), 60.7 is not
    # (nan and inf also fail this check, so they're rejected too)
    if not number.is_integer():
        raise ValidationError(f"{field_name} must be a whole number, got {value!r}")

    return int(number)

def _clean_text(value, field_name):
    """Return value as stripped text. Reject None and empty values."""
    # Check None BEFORE str(): str(None) would give the text "None"
    if value is None:
        raise ValidationError(f"{field_name} is required.")

    text = str(value).strip()
    if not text:
        raise ValidationError(f"{field_name} can't be empty.")
    return text  

class StudyTracker:
    def __init__(self, filepath):
        self.filepath = Path(filepath)

    def load(self):
        """Return the study log as a DataFrame. Create the file on first run."""
        try:
            if not self.filepath.exists():
                 self.filepath.parent.mkdir(parents=True, exist_ok=True)

                 empty_df = pd.DataFrame(columns=COLUMNS)
                 empty_df.to_csv(self.filepath, index=False)
                 return empty_df
            
            df = pd.read_csv(self.filepath)

            if set(df.columns) != set(COLUMNS):
                raise StorageError(
                    f"Unexpected columns in {self.filepath}. "
                    f"Expected {COLUMNS}, Found {list(df.columns)}"
                )

            df["Date"] = pd.to_datetime(df['Date'])

        except (OSError, ValueError) as e:
            raise StorageError(f"Could not read {self.filepath}: {e}") from e
        
        return df[COLUMNS]

    def save(self, df):
        """Write the DataFrame to the csv file."""

        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.filepath, index=False, date_format="%Y-%m-%d")
        except OSError as e:
            raise StorageError(f'Could not write {self.filepath}: {e}') from e

    def add_session(self, date, category, subject, minutes, understanding, notes=''):
        """Validate one studying session, append it to the log, and save"""

        # 1) Validate everything:
        # Date: Must be convertible to a real date
        # The function clean_date() from base_tracker validate it
        date = clean_date(date)
        # Textfileds: strip spaces and don't allow empty values
        category = _clean_text(category, "Category")
        subject = _clean_text(subject, "Subject")
         # reject subjects made only of digits
        if subject.isdigit():
            raise ValidationError("Subject can't be only numbers. Describe what you studied.")
        # Minutes: Must be a whole number between 1 and MAX_MINUTES
        minutes = _whole_number(minutes, "Minutes")
        if not 1 <= minutes <= MAX_MINUTES:
            raise ValidationError(f"Minutes must be between 1 and {MAX_MINUTES}")
        #Understanding: Must be a number between 1 and 5
        understanding = _whole_number(understanding, "Understanding")
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
        df = self.load()
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True)

        self.save(df)


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

    
        