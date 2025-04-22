import requests
from collections import Counter

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
