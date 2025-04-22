import streamlit as st
from utils import fetch_all_emotion_data, summarize_emotions
import matplotlib.pyplot as plt

st.set_page_config(page_title="Teacher Dashboard", layout="wide")
st.title("Real-Time Classroom Emotion Dashboard")

API_URL = "https://student-api-emk4.onrender.com/all"

st.markdown("Click the button below to fetch latest student emotion summaries:")

if st.button("Refresh Emotion Results"):
    all_data = fetch_all_emotion_data(API_URL)
    emotion_summary = summarize_emotions(all_data)

    if emotion_summary:
        st.subheader("Aggregate Emotion Distribution")
        fig, ax = plt.subplots()
        ax.bar(emotion_summary.keys(), emotion_summary.values(), color='skyblue')
        ax.set_xlabel("Emotions")
        ax.set_ylabel("Frequency")
        ax.set_title("Summary of Student Emotions")
        st.pyplot(fig)
    else:
        st.warning("No emotion data received yet.")
