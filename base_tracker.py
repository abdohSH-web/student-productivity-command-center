from pathlib import Path
import pandas as pd 

# shared errors
class StorageError(Exception):
    """Raised when the CSV file can't be read/written or has a wrong structure"""

class ValidationError(Exception):
    """Raised when the data the user entered is not valid"""

MAX_MINUTES = 24 * 60

# Shared sanity limit for calories in a single meal or a single workout
MAX_CALORIES = 5000

def clean_date(value):
    """Convert value to a real date. Reject None, empty text, and invalid dates."""
    if value is None:
        raise ValidationError("Date can't be empty")
    try:
        result = pd.to_datetime(value)
    except(ValueError, TypeError) as e:
        raise ValidationError(f"Invalid date {value!r}") from e
    if pd.isna(result):
        raise ValidationError(f"Invalid date {value!r}")
    return result



# shated validation helpers
def whole_number(value, field_name):
    """Convert value into an int, but reject any declaims instead of silently cutting them."""

    try:
        number = float(value)
    except(ValueError, TypeError) as e:
        raise ValidationError(f"{field_name} must be a number, got {value!r}") from e

    if not number.is_integer():
        raise ValidationError(f"{field_name} must be a whole number, got {value!r}")
    
    return int(number)

def clean_text(value, field_name):
    """Return value as stripped text. Reject None and empty values."""
    if value is None:
        raise ValidationError(f"{field_name} is required")

    text = str(value).strip()
    if not text:
        raise ValidationError(f"{field_name} can't be empty")

    return text

# Parent class
class BaseTracker:
    # Class attributes: each child class OVERRIDES COLUMNS with its own list.
    # An empty list here means "not defined yet".
    COLUMNS = []
    DATE_COLUMN = 'Date'

    def __init__(self, filepath):
        # If a child class forgets to define COLUMNS, fail loudly now
           # instead of creating a broken CSV file later.
       if not self.COLUMNS:
           raise NotImplementedError(f"{type(self).__name__} must define its own COLUMNS list.")
       self.filepath = Path(filepath)

    def load(self):
        """Return the log as a DataFrame. Create the file on first run."""
        try: 
            if not self.filepath.exists():
                self.filepath.parent.mkdir(parents=True, exist_ok=True)
                empty_df = pd.DataFrame(columns=self.COLUMNS)
                empty_df.to_csv(self.filepath, index=False)
                return empty_df
            df = pd.read_csv(self.filepath)

            # Check structure before touching any column
            if set(df.columns) != set(self.COLUMNS):
                raise StorageError(
                    f"Unexpected columns in {self.filepath}. "
                    f"Expected {self.COLUMNS}, found {list(df.columns)}"
                )
            df[self.DATE_COLUMN] = pd.to_datetime(df[self.DATE_COLUMN])

        except(OSError, ValueError) as e:
            raise StorageError(f"Could not read {self.filepath}: {e}") from e
        return df[self.COLUMNS]

    def save(self, df):
        """Write the DataFrame to the csv file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.filepath, index=False, date_format='%Y-%m-%d')
        except OSError as e :
            raise StorageError(f"Could not write {self.filepath}: {e}") from e

    def append_row(self, new_row):
        """Add one already-validated row (a one-row DataFrame) and save."""
        df = self.load()
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True)
        self.save(df)

    

        




