import pandas as pd

from base_tracker import ValidationError, clean_text
from storage import StorageError

# Text that pandas silently turns into "missing" when it reads a CSV
RESERVED_NAMES = {"na", "n/a", "nan", "null", "none", "nat"}


class OptionList:
    """A list of choices (category, activity), that the user can edit.
    it saves itself through any Storage object, just like the trackers do."""

    COLUMN = "Name"
    MAX_OPTION = 20
    MAX_LENGTH = 30

    def __init__(self, storage, defaults):
        self.storage = storage
        self.defaults = list(defaults)

    def get(self):
        """Return the current options as a list of strings"""
        raw = self.storage.read() #may raise a StorageError

        if raw is None:
            self._save(self.defaults)
            return list(self.defaults)

        if self.COLUMN not in raw.columns:
            raise StorageError(f"Unexpected columns in {self.storage}: {list(raw.columns)}")

        return raw[self.COLUMN].dropna().astype(str).tolist()

    def add(self, name):
        """Add a new option. Rejects empty, too long, reserved and duplicate names."""
        name = clean_text(name, "Name")    #reject None and empty text
        name = " ".join(name.split())

        if len(name) > self.MAX_LENGTH:
            raise ValidationError(f"Name is too long (Max {self.MAX_LENGTH} characters).")
        if name.casefold() in RESERVED_NAMES:
            raise ValidationError(f"'{name}' can't be used as a name, please choose another.")

        options = self.get()
        if len(options) >= self.MAX_OPTION:
            raise ValidationError(f"You can have at most {self.MAX_OPTION} options.")

        # casefold() compares ignoring letter case: "python" matches "Python"
        if name.casefold() in (option.casefold() for option in options):
            raise ValidationError(f"'{name}' already exists.")

        self._save(options + [name])

    def remove(self, name):
        """Remove an option. At least one must always remain."""
        options = self.get()
        if name not in options:
            raise ValidationError(f"'{name}' is not in the list.")
        if len(options) == 1:
            raise ValidationError("You need at least one option.")

        self._save([option for option in options if option != name])

    def _save(self, options):
        self.storage.write(pd.DataFrame({self.COLUMN: options}))
        

