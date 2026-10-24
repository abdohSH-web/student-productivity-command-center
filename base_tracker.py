from storage import Storage, StorageError
import pandas as pd 


# shared errors


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

    def __init__(self, storage):
        if not self.COLUMNS:
            raise NotImplementedError(
                f"{type(self).__name__} must define its own COLUMNS list"
            )
        # Clear error if someone still passes a file path
        if not isinstance(storage, Storage):
            raise TypeError(
                "Pass a storage object, e.g. CSVStorage(data/log.csv), "
                f"not {type(self).__name__}."
            )
        self.storage = storage

    def load(self):
        """Return the log as a DataFrame. Create it on first run."""
        raw = self.storage.read()
        # first run, nothing stored yet. Start with an empty table
        if raw is None:
            empty_df = pd.DataFrame(columns=self.COLUMNS)
            self.storage.write(empty_df)
            return empty_df
        # check structure first
        if set(raw.columns) != set(self.COLUMNS):
            raise StorageError(
                f"Unexpected columns in {self.storage}. "
                f"Expected {self.COLUMNS}, found {list(raw.columns)}"
            )

        try:
            raw[self.DATE_COLUMN] = pd.to_datetime(raw[self.DATE_COLUMN])
        except ValueError as e:
            raise StorageError(f"Invalid dates in {self.storage}: {e}") from e
        return raw[self.COLUMNS]

    def save(self, df):
        """Write the DataFrame to the storage."""
        self.storage.write(df)
       
    def append_row(self, new_row):
        """Add one already-validated row (a one-row DataFrame) and save."""
        df = self.load()
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True)
        self.save(df)

    

        




