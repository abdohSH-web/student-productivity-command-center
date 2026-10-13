from pathlib import Path
import pandas as pd

COLUMNS = ['Date','Category','Subject','Time','Understanding','Notes']
MAX_MINUTES = 24 * 60

class StorageError(Exception):
    """Raised when the CSV file can't be read/written or has a wrong structure"""

class ValidationError(Exception):
    """Raised when the data the user entered is not valid"""

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
        try: 
            date = pd.to_datetime(date)
        except(ValueError, TypeError) as e:
            raise ValidationError(f"Invalid date: {date!r}") from e
        # Textfileds: strip spaces and don't allow empty values
        category = str(category).strip()
        subject = str(subject).strip()
        if (not category or not subject):
            raise ValidationError("Category and Subject can't be empty.")
        # Minutes: Must be a whole number between 1 and MAX_MINUTES
        try:
            minutes = int(minutes)
        except(ValueError, TypeError) as e:
            raise ValidationError(f"Minutes must be a number, got {minutes!r}") from e
        if not 1 <= minutes <= MAX_MINUTES:
            raise ValidationError(f"Minutes must be between 1 and {MAX_MINUTES}")
        #Understanding: Must be a number between 1 and 5
        try:
            understanding = int(understanding)
        except(ValueError, TypeError) as e:
            raise ValidationError(f"Understanding must be a number, got {understanding!r}") from e
        if not 1<= understanding <=5 :
            raise ValidationError(f"Understanding must be a number between 1 and 5")
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
    tracker.add_session("2026-10-12", "Python", "file I/O", 60, 4, "Good session")
    print(tracker.load())

    # An invalid session: our ValidationError should catch it
    try:
        tracker.add_session("2026-10-12", "Python", "OOP", -5, 4)
    except ValidationError as e:
        print("Rejected:", e)

    
        