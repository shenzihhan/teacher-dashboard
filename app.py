from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import requests

# -------------------- Utils --------------------
def fetch_all_emotion_data(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return []

def summarize_emotions(data):
    emotion_counter = Counter()
    for entry in data:
        emotions = entry.get("emotions", {})
        emotion_counter.update(emotions)
    return dict(emotion_counter)

def parse_trend(data):
    trend = {}
    for entry in data:
        ts = entry.get("timestamp", "unknown")
        emotions = entry.get("emotions", {})
        for emo, count in emotions.items():
            trend.setdefault(ts, {}).setdefault(emo, 0)
            trend[ts][emo] += count
    return trend

def suggest_teaching_action(summary):
    suggestions = []
    if summary.get("sad", 0) + summary.get("fear", 0) >= 3:
        suggestions.append("Students may feel anxious. Try using encouraging language or adding a break.")
    if summary.get("neutral", 0) > max(summary.get("happy", 0), 2):
        suggestions.append("Most students are neutral. Consider more engagement or interaction.")
    if summary.get("happy", 0) >= 5:
        suggestions.append("Great! Students seem highly engaged.")
    if summary.get("angry", 0) >= 2:
        suggestions.append("Anger detected. Consider asking for feedback or reviewing content clarity.")
    return suggestions

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Teacher Dashboard", layout="wide")
st.title("Teacher Dashboard: Class Emotion Summary")

st.markdown("Click the button below to load student emotion results.")

if st.button("Load Student Emotion Data"):
    API_ENDPOINT = "https://student-api-emk4.onrender.com/all"
    all_data = fetch_all_emotion_data(API_ENDPOINT)

    if not all_data:
        st.error("No data found or failed to fetch from API.")
    else:
        st.success(f"{len(all_data)} student records loaded.")

        # Total emotion count
        summary = summarize_emotions(all_data)
        df_summary = pd.DataFrame(summary.items(), columns=["Emotion", "Count"])

        # Pie chart
        st.subheader("Overall Emotion Distribution")
        fig1, ax1 = plt.subplots()
        ax1.pie(df_summary["Count"], labels=df_summary["Emotion"], autopct="%1.1f%%")
        st.pyplot(fig1)

        # Bar chart
        st.subheader("Emotion Frequency")
        fig2, ax2 = plt.subplots()
        ax2.bar(df_summary["Emotion"], df_summary["Count"], color="skyblue")
        st.pyplot(fig2)

        # Time-based emotion trend (if timestamp is present)
        trend_data = parse_trend(all_data)
        if trend_data:
            df_trend = pd.DataFrame.from_dict(trend_data, orient="index").fillna(0)
            df_trend.index = pd.to_datetime(df_trend.index)
            df_trend.sort_index(inplace=True)

            st.subheader("Emotion Trend Over Time")
            fig3, ax3 = plt.subplots()
            df_trend.plot(ax=ax3, marker="o")
            plt.xticks(rotation=45)
            st.pyplot(fig3)

        # Teaching Suggestions
        st.subheader("Teaching Suggestions")
        suggestions = suggest_teaching_action(summary)
        if suggestions:
            for s in suggestions:
                st.info(f"- {s}")
        else:
            st.success("No major concerns detected. Keep up the good work!")
