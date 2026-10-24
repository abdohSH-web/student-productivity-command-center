import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path

class StorageError(Exception):
    """Raised when stored data can't be read or written."""

class Storage(ABC):
    @abstractmethod
    def read(self):
        """Return the stored DataFrame. Or None if nothing has been stored yet."""

    @abstractmethod
    def write(self, df):
        """Store the DataFame, replacing whatever was stored before."""

# Local files: the read data
class CSVStorage(Storage):
    def __init__(self, filepath):
        self.filepath = Path(filepath)

    def __str__(self):
        # Used in s error messages
        return str(self.filepath)

    def read(self):
        if not self.filepath.exists():
            return None                 #Nothing stored yet, not an error
        try:
            return pd.read_csv(self.filepath)
        except(OSError, ValueError) as e:
            raise StorageError (f"Could not read {self.filepath}: {e}") from e

    def write(self, df):
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.filepath, index=False, date_format="%Y-%m-%d")
        except OSError as e:
            raise StorageError(f"Could not write {self.filepath}: {e}") from e


# Pre-visitor memory: for the public demo
class SessionStorage(Storage):
    def __init__(self, state, key):
        self.state = state
        self.key = key

    def __str__(self):
        return f"session: {self.key}"

    def read(self):
        df = self.state.get(self.key)
        # Return a COPY: if the caller changes it, the stored data stays safe
        return None if df is None else df.copy()

    def write(self, df):
        self.state[self.key] = df.copy()
        

        
        
        

