import streamlit as st
from datetime import date

from base_tracker import StorageError, ValidationError, MAX_MINUTES, MAX_CALORIES
from study_tracker import StudyTracker
from workout_tracker import WorkoutTracker
from meal_tracker import MealTracker
from analytics import minutes_per_category, minutes_per_week, average_understanding



CATEGORIES = ['Programming','English Language','Graphic Design','University','Other']

tracker = StudyTracker('./data/study_log.csv')

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
            tracker.add_session(session_date, category, subject, time, understanding, notes)
            st.success("Saved sussion ✅")
        except ValidationError as e:
            st.warning(f"Please check your input: {e}")
        except StorageError as e:
            st.warning(f"Storage problem: {e}")

    st.subheader("Your session")
    try:
        df = tracker.load()
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

workout_tracker = WorkoutTracker("data/workout_log.csv")
meal_tracker = MealTracker("data/meals_log.csv")

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
        show_log(workout_tracker, "No workouts yet. Log your first one above")

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
        show_log(meal_tracker, 'No meals yet. Log your first one above')

# The page itself, three tabs, one function per tab
tab_study, tab_workout, tab_meals = st.tabs(["📚 Study", "💪 Workout", "🍽️ Meals"])

with tab_study:
    study_tab()
with tab_workout:
    workout_tab()
with tab_meals:
    meals_tab()

            

    



    


