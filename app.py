import streamlit as st
from datetime import date
import pandas as pd
import os
from storage import CSVStorage, SessionStorage

from base_tracker import StorageError, ValidationError, MAX_MINUTES, MAX_CALORIES
from study_tracker import StudyTracker
from workout_tracker import WorkoutTracker
from meal_tracker import MealTracker
from analytics import minutes_per_category, minutes_per_week, average_understanding, total_per_period, filter_recent, activity_summary, intake_vs_burn

st.set_page_config(page_title="Command Center", page_icon="📚")
st.title("Student & Productivity Command Center")

STORAGE_MODE = os.environ.get("STORAGE_MODE", 'cvs')

def make_storage(name):
    """Pick the storage for the tracker based on the mode."""
    if STORAGE_MODE == "session":
        return SessionStorage(st.session_state, name)
    return CSVStorage(f"data/{name}.csv")

if STORAGE_MODE == 'session':
    st.info(
        "Demo mode: your data is kept only in this browser session "
        "and disappears when you refresh or close the page."
    )


CATEGORIES = ['Programming','English Language','Graphic Design','University','Other']

study_tracker = StudyTracker(make_storage('study_log'))

def study_tab():
    # Page setup
    st.set_page_config(page_title='Study Tracker', page_icon="📚")
    st.title("Study Tracker 📚")

    st.subheader("Log a session")

    with st.form('study_form'):
        session_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", CATEGORIES)
        subject = st.text_input("Subject", placeholder='eg. Pandas grouby')
        time = st.number_input("Time in minutes", min_value=1, max_value=MAX_MINUTES, value=30, step=5)
        understanding = st.slider("How well you understand (1=Lost, 5=Got it)", 1, 5, 3)
        notes =  st.text_area('Notes (Optional)')

        submitted = st.form_submit_button("Save session")

    if submitted:
        try:
            study_tracker.add_session(session_date, category, subject, time, understanding, notes)
            st.success("Saved sussion ✅")
        except ValidationError as e:
            st.warning(f"Please check your input: {e}")
        except StorageError as e:
            st.warning(f"Storage problem: {e}")

    st.subheader("Your session")
    try:
        df = study_tracker.load()
        if df.empty:
            st.info("No session yet, log  your first one above")
        else:
            st.dataframe(df.sort_values("Date", ascending=False), hide_index=True)

            st.subheader("Summary")

            # two charts, side by side
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Minutes per category")
                st.bar_chart(minutes_per_category(df))
            with col2:
                st.caption("Minutes per week")
                st.bar_chart(minutes_per_week(df))

            st.caption("Average understanding (1-5) per week")
            st.bar_chart(average_understanding(df))

            

    except StorageError as e:
        st.error(f"Could not load your log: {e}")

ACTIVITIES = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Cardio", "Other"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]
PERIOD_DAYS = {"Last 7 days": 7, "Last 30 days": 30, "All time": None}


workout_tracker = WorkoutTracker(make_storage("workout_log"))
meal_tracker = MealTracker(make_storage("meals_log"))

def show_log(tracker, empty_message):
    """Load a tracker's log and show it as a table, newest first.
    Returns the DataFrame (or None), so a caller can build summaries from it."""

    try:
        df = tracker.load()
    except StorageError as e:
        st.error(f"Could not load the log: {e}")
        return None

    if df.empty:
        st.info(empty_message)
        return None

    st.dataframe(df.sort_values("Date", ascending=False), hide_index=True)
    return df

def workout_tab():
    st.set_page_config(page_title='Workout Tracker', page_icon="🏋️")
    st.title("Workout Tracker 🏋️")
    st.subheader("Log a workout")

    with st.form("Workout_form"):
        w_date = st.date_input("Date",value=date.today(), key='w_date')
        activity = st.selectbox("Activity", ACTIVITIES, key='w_activity')
        minutes = st.number_input(
            "Minutes", min_value=1, max_value=MAX_MINUTES, value=45, step=5, key='w_minutes'
        )
        intensity = st.slider("Intensity (1 = light, 5 = very hard)",1, 5, 3, key='w_intensity')
        calories_burned = st.number_input("Calories_burned", min_value=0, max_value=MAX_CALORIES, value=0, step=10, key='w_calories_burned')
        notes = st.text_area("Notes (Optional)", key='w_notes')
        submitted = st.form_submit_button("Save workout")

        if submitted:
            try:
                workout_tracker.add_workout(w_date,activity,minutes,intensity,calories_burned=calories_burned,notes=notes)
                st.success("Workout saved")
            except ValidationError as e:
                st.warning(f"Please check your input: {e}")
            except StorageError as e:
                st.error(f"Storage problem: {e}")

        st.subheader("Your workouts")
        df = show_log(workout_tracker, "No workouts yet. Log your first one above")
        if df is not None:
            st.subheader("Summary")

            period = st.radio("Period", list(PERIOD_DAYS), horizontal=True, key="w_period")
            recent = filter_recent(df, PERIOD_DAYS[period])

            st.dataframe(activity_summary(recent))

            st.caption("Minutes per week")
            st.bar_chart(total_per_period(df, "Time", "W"))

def meals_tab():
    st.set_page_config(page_title='Meals Tracker', page_icon="🍽️")
    st.title("Workout Tracker 🍽️")
    st.subheader("Log a meal")

    with st.form("meal_form"):
        m_date = st.date_input("Date", value=date.today(), key='m_date')
        meal = st.selectbox("Meal", MEAL_TYPES, key='m_meal')
        food = st.text_input('Food', placeholder='e.g Chicken and rice', key='m_food')
        calories = st.number_input(
            "Calories", min_value=1, max_value=MAX_CALORIES, value=500, step=10, key='m_calories'
        )
        submitted = st.form_submit_button("Save meal")
        if submitted:
            try:
                meal_tracker.add_meal(m_date, meal, food, calories)
                st.success("Meal saved")
            except ValidationError as e:
                st.warning(f"Please check your input: {e}")
            except StorageError as e:
                st.error(f"Storage problem: {e}")

        st.subheader("Your meal")
        df = show_log(meal_tracker, 'No meals yet. Log your first one above')
        if df is not None:
            st.subheader("Summary")

            today_total = df[df["Date"] == pd.Timestamp.today().normalize()]["Calories"].sum()
            st.metric("Calories today", int(today_total))

            st.caption("Calories per day")
            st.bar_chart(total_per_period(df, "Calories", "D"))

def overview_tab():
    st.subheader("Calories: eaten vs burned in workouts")
    st.caption(
        "Burned calories are your own estimates and cover workouts only, and 0 means "
        "'not tracked'. So this is a comparison, not a full energy balance."
    )

    view = st.radio("View", ["Weekly", "Monthly"], horizontal=True, key="o_view")
    period = "W" if view == "Weekly" else "M"

    try:
        meals_df = meal_tracker.load()
        workouts_df = workout_tracker.load()
    except StorageError as e:
        st.error(f"Could not load your logs: {e}")
        return    #Stop here, nothing to draw without data

    combined = intake_vs_burn(meals_df, workouts_df, period)
    if combined.empty:
        st.info("Log some meals or workouts first.")
        return

    st.bar_chart(combined)
    st.dataframe(combined)


# The page itself, three tabs, one function per tab
tab_study, tab_workout, tab_meals, tab_overview = st.tabs(["📚 Study", "💪 Workout", "🍽️ Meals", "📊 Overview"])

with tab_study:
    study_tab()
with tab_workout:
    workout_tab()
with tab_meals:
    meals_tab()
with tab_overview:
    overview_tab()


            

    



    


