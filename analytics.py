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

def _empty_series():
    """An empty RESULT that is still a Series (with a datetime index)."""
    return pd.Series(dtype='int64', index=pd.DatetimeIndex([]))

def total_per_period(df, value_col, period):
    """Sum value_col per day ("D"), week ("W"), or Month ("M")"""
    """Each period is labelled by its first day (Monday for week, First day for month)"""
    if df.empty:
        return _empty_series()
    period_start = df["Date"].dt.to_period(period).dt.start_time
    return df.groupby(period_start)[value_col].sum()

def filter_recent(df, days):
    if df.empty or days is None:
        return df
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=days - 1)
    return df[df["Date"] >= cutoff]

def activity_summary(df):
    """Per activity, number of session, total minutes, and average intensity"""
    if df.empty:
        return pd.DataFrame(columns=['Sessions','Minutes','Avg_intensiry'])
    return (
        df.groupby("Activity")
        .agg(
            Sessions=('Date', 'count'),
            Minutes=("Time", "sum"),
            Avg_intensity=("Intensity", "mean"),
        )
        .round(2)
        .sort_values("Sessions", ascending=False)
    )

def intake_vs_burn(meals_df, workout_df, period):
    """Calories eaten vs calories burned in workouts, per week ("W"), or month ("M")."""
    eaten = total_per_period(meals_df, "Calories", period)
    burned = total_per_period(workout_df, "Calories_burned", period)

    # Building a DataFrame from a dict of Series LINES THEM UP by index (the dates).
    # A period that exists in only one of them gets NaN in the other column,
    # so we turn those into 0 and make everything whole numbers again.
    combined = pd.DataFrame({"Eaten": eaten, "Burned in workouts": burned})
    return combined.fillna(0).astype(int)


