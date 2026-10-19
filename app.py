import streamlit as st
from datetime import date

from study_tracker import StudyTracker, StorageError, ValidationError, MAX_MINUTES
from analytics import minutes_per_category, minutes_per_week, average_understanding

# Page setup
st.set_page_config(page_title='Study Tracker', page_icon="📚")
st.title("Study Tracker 📚")

CATEGORIES = ['Programming','English Language','Graphic Design','University','Other']

tracker = StudyTracker('./data/study_log.csv')

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




