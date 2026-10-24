# Student & Productivity Command Center

A mobile-friendly web app for tracking study sessions, workouts and meals, with weekly and monthly analytics. Built with Python, Streamlit and Pandas.

**Live demo:** [your-app-link].streamlit.app

## Features

- **Study tracker:** log sessions by category, with time and a 1–5 understanding rating; weekly totals per category.
- **Workout log:** log activities with duration, intensity and estimated calories burned; per-activity summaries over 7 days, 30 days or all time.
- **Meal log:** log meals with calories; daily totals.
- **Overview:** weekly and monthly comparison of calories eaten and calories burned in workouts.

## Architecture

- storage.py – storage layer: an abstract Storage class with CSVStorage (local files) and SessionStorage (per-visitor session data).
- base_tracker.py – BaseTracker, the shared parent class: loading, structure checks, date handling and appending rows. Also holds the shared validation helpers and error types.
- study_tracker.py, workout_tracker.py, meal_tracker.py – child classes that only define their columns and validation rules.
- analytics.py – Pandas aggregations (groupby, period totals, summaries), kept separate from data management.
- app.py – the Streamlit interface.

## Design decisions

- **Validation before storage:** every input is validated before the file is touched, so bad data can never reach the log.
- **Custom errors:** ValidationError (fix your input) and StorageError (a problem with the data) are shown differently in the interface.
- **Pluggable storage:** trackers receive a storage object instead of a file path. The public demo uses session storage, so visitors never see each other's data.

## Run locally

​
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
​

Your data is saved in the data/ folder (not tracked by Git).

To try the demo mode locally: set the environment variable STORAGE_MODE=session before running.

## Screenshots

[add screenshots here]