from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import requests
import streamlit as st

# -------------------- Utility Functions --------------------
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
    all_emotions = []
    for entry in data:
        all_emotions.extend(entry.get("emotions", []))
    emotion_counter = Counter(all_emotions)
    return dict(emotion_counter)

def parse_trend(data):
    trend = {}
    for entry in data:
        ts = entry.get("timestamp", "unknown")
        emotions = entry.get("emotions", [])
        counter = Counter(emotions)
        for emo, count in counter.items():
            trend.setdefault(ts, {}).setdefault(emo, 0)
            trend[ts][emo] += count
    return trend

def parse_attention_trend(data):
    trend = {}
    for entry in data:
        ts = entry.get("timestamp", "unknown")
        attention = entry.get("attention", 0)
        trend[ts] = attention
    return trend

def suggest_teaching_action(summary, attention_data):
    suggestions = []

    if summary.get("sad", 0) + summary.get("fear", 0) >= 3:
        suggestions.append("😟 Several students appeared sad or afraid. Start next class with encouragement.")
    if summary.get("neutral", 0) > max(summary.get("happy", 0), 2):
        suggestions.append("😐 Many students felt neutral. Try more interaction or visual aids.")
    if summary.get("happy", 0) >= 5:
        suggestions.append("😊 Students were highly engaged. Continue this with discussions.")
    if summary.get("angry", 0) >= 2:
        suggestions.append("😡 Anger detected. Clarify confusing topics and request feedback.")

    if attention_data:
        avg_attention = sum(attention_data.values()) / len(attention_data)
        if avg_attention < 0.5:
            suggestions.append("Low attention detected. Consider short breaks or small groups.")
        elif avg_attention >= 0.8:
            suggestions.append("Excellent attention levels. Use this for deep dives or harder tasks.")
        else:
            suggestions.append("Moderate attention. Use real-life examples to boost engagement.")

    return suggestions

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Teacher Dashboard", layout="wide")
st.title("Teacher Dashboard: Class Emotion Summary")

st.markdown("Click below to fetch the latest student emotion results:")

if st.button("Load Student Emotion Data"):
    API_ENDPOINT = "https://student-api-emk4.onrender.com/all"
    all_data = fetch_all_emotion_data(API_ENDPOINT)

    if not all_data:
        st.error("No data found or failed to fetch from API.")
    else:
        st.success(f"Loaded {len(all_data)} student submissions.")

        summary = summarize_emotions(all_data)
        df_summary = pd.DataFrame(summary.items(), columns=["Emotion", "Count"])

        st.subheader("1. Overall Emotion Distribution")
        fig1, ax1 = plt.subplots()
        ax1.pie(df_summary["Count"], labels=df_summary["Emotion"], autopct="%1.1f%%", startangle=140)
        st.pyplot(fig1)

        st.subheader("2. Emotion Frequency Bar Chart")
        fig2, ax2 = plt.subplots()
        ax2.bar(df_summary["Emotion"], df_summary["Count"], color="skyblue")
        ax2.set_ylabel("Number of Occurrences")
        st.pyplot(fig2)

        trend_data = parse_trend(all_data)
        if trend_data:
            df_trend = pd.DataFrame.from_dict(trend_data, orient="index").fillna(0)
            df_trend.index = pd.to_datetime(df_trend.index)
            df_trend.sort_index(inplace=True)

            st.subheader("3. Emotion Trend Over Time")
            fig3, ax3 = plt.subplots()
            df_trend.plot(ax=ax3, marker="o")
            ax3.set_ylabel("Emotion Count")
            plt.xticks(rotation=45)
            st.pyplot(fig3)

        attention_data = parse_attention_trend(all_data)
        if attention_data:
            st.subheader("4. Class Attention Over Time")
            df_attention = pd.DataFrame(list(attention_data.items()), columns=["Timestamp", "Attention"])
            df_attention["Timestamp"] = pd.to_datetime(df_attention["Timestamp"])
            df_attention.set_index("Timestamp", inplace=True)
            df_attention.sort_index(inplace=True)

            fig4, ax4 = plt.subplots()
            df_attention.plot(ax=ax4, marker='o', color='orange')
            ax4.set_ylabel("Attention (0 = Low, 1 = High)")
            plt.xticks(rotation=45)
            st.pyplot(fig4)

        st.subheader("5. AI-Powered Teaching Suggestions")
        suggestions = suggest_teaching_action(summary, attention_data)
        if suggestions:
            for s in suggestions:
                st.info(f"- {s}")
        else:
            st.success("No major concerns. Students appear engaged.")
