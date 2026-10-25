from storage import Storage, StorageError, SessionStorage
import pandas as pd 


# shared errors


class ValidationError(Exception):
    """Raised when the data the user entered is not valid"""

MAX_MINUTES = 24 * 60

# Shared sanity limit for calories in a single meal or a single workout
MAX_CALORIES = 5000
# Safety cap on uploaded files (re-checking every row takes time)
MAX_IMPORT_ROWS = 2000

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

    def export_csv(self):
        """Return the log as csv text, ready for a download button."""
        return self.load().to_csv(index=False, date_format="%Y-%m-%d")
    
    def add_from_row(self, row):
        """Add one row (a dict) read from an uploaded file.
        Each child class says how its columns map to its own add_* method."""
        raise NotImplementedError(f"{type(self).__name__} must implement add_from_row.")

    def import_csv(self, file):
        """Replace the log with the rows of an uploaded CSV. All or nothing."""
        #1) read the file, anything unreadable becomes a clear ValidationError.
        try:
            uploaded = pd.read_csv(file)
        except (ValueError, OSError) as e:
            raise ValidationError(f"This doesn't look like a valid CSV file: {e}") from e

        #2) check its structure and size:
        if set(uploaded.columns) != set(self.COLUMNS):
            raise ValidationError(
                f"Wrong columns. Expected {self.COLUMNS}, found {list(uploaded.columns)}."
            )
        if len(uploaded) > MAX_IMPORT_ROWS:
            raise ValidationError(f"Too many rows. (Max {MAX_IMPORT_ROWS}).")
        
        #empty cells like empty notes, arrive as NaN; turn them into ""
        uploaded = uploaded[self.COLUMNS].fillna("")

        #3) re-validate every row in a temporary in-memory tracker of the same type
        scratch = type(self)(SessionStorage({}, "import"))
        for number, row in enumerate(uploaded.to_dict("records"), start=1):
            try:
                scratch.add_from_row(row)
            except ValidationError as e:
                raise ValidationError(f"Row {number}: {e}") from e

        #4) now that everything passed, replace the data
        self.save(scratch.load())





    

        




