import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

API_ENDPOINT = "https://student-api-emk4.onrender.com/all"

st.set_page_config(page_title="Teacher Emotion Dashboard", layout="centered")
st.title("Classroom Emotion Summary Dashboard")

if st.button("View Dashboard Results"):
    try:
        res = requests.get(API_ENDPOINT)
        if res.status_code != 200:
            st.error("Failed to fetch data from API.")
        else:
            json_data = res.json()
            if not json_data:
                st.info("No data available yet.")
            else:
                df = pd.DataFrame(json_data)

                # Combine emotion counts across students
                total_emotions = {}
                for item in df["emotions"]:
                    for emo, count in item.items():
                        total_emotions[emo] = total_emotions.get(emo, 0) + count

                # Pie chart
                st.subheader("Overall Emotion Distribution")
                fig1, ax1 = plt.subplots()
                ax1.pie(total_emotions.values(), labels=total_emotions.keys(), autopct='%1.1f%%')
                st.pyplot(fig1)

                # Bar chart
                st.subheader("Total Emotion Counts")
                fig2, ax2 = plt.subplots()
                ax2.bar(total_emotions.keys(), total_emotions.values(), color='skyblue')
                ax2.set_ylabel("Count")
                st.pyplot(fig2)

                # Line chart by upload time (simulate emotion over time)
                st.subheader("Emotion Trend Over Upload Time")
                df_sorted = df.sort_values("timestamp")
                emotion_df = pd.DataFrame(df_sorted["emotions"].tolist())
                emotion_df["timestamp"] = pd.to_datetime(df_sorted["timestamp"])
                emotion_df = emotion_df.set_index("timestamp").fillna(0)
                fig3, ax3 = plt.subplots()
                emotion_df.plot(ax=ax3)
                ax3.set_ylabel("Emotion Count")
                st.pyplot(fig3)

                # Automated teacher suggestion
                st.subheader("Teaching Suggestions")
                suggestions = []
                if total_emotions.get("neutral", 0) >= sum(total_emotions.values()) * 0.4:
                    suggestions.append("Many students appear neutral. Consider using more interactive or engaging activities.")
                if total_emotions.get("happy", 0) >= sum(total_emotions.values()) * 0.4:
                    suggestions.append("Students appear engaged and happy. Current teaching methods are effective.")
                if total_emotions.get("sad", 0) >= 2 or total_emotions.get("angry", 0) >= 2:
                    suggestions.append("Some students show negative emotions. Consider checking in with the class or using anonymous feedback.")
                if total_emotions.get("surprise", 0) >= 3:
                    suggestions.append("High surprise detected. Ensure clarity of complex concepts.")

                for s in suggestions:
                    st.markdown(f"- {s}")

    except Exception as e:
        st.error(f"Error connecting to API: {e}")
