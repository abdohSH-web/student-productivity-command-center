import pandas as pd

def minutes_per_category(df):
    """Total minutes for each category, biggest first."""
    if df.empty:
        return pd.Series(dtype="int64")
    return df.groupby('Category')['Time'].sum().sort_values(ascending=False)

def minutes_per_week(df):
    """Total minutes for each week, each week is labelled by its Monday."""
    if df.empty:
        return pd.Series(dtype="int64")
    week_start = df['Date'].dt.to_period("W").dt.start_time
    return df.groupby(week_start)['Time'].sum()

def average_understanding(df):
    """Average understanding score (1-5) for each category"""
    if df.empty:
        return pd.Series(dtype="float64")
    return df.groupby("Category")['Understanding'].mean().round(2)