import json

import pyttsx3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

from jarvis import query_llm_for_memory

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend to access API

# Initialize API Client
api_client = genai.Client(api_key="AIzaSyAAQB7cXM63W2KV7Xz7maEpBJAWm4Y4b6Q")

# Memory File
memory_file = "memory.json"


def load_memory():
    try:
        with open(memory_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"history": []}


conversations = load_memory()


def save_memory(conversations):
    with open(memory_file, "w") as f:
        json.dump(conversations, f, indent=4)


def store_conversation(user_query, jarvis_response):
    conversations["history"].append({"user": user_query, "jarvis": jarvis_response})
    save_memory(conversations)


# Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[0].id)


def say(text):
    engine.say(text)
    engine.runAndWait()
    return text


@app.route('/')
def home():
    return "Jarvis API is running!"


@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    query = data.get('query', '').lower()
    response = ""

    if 'weather' in query:
        city = data.get('city', 'Rajkot')  # Default city if not provided
        response = get_weather(city)

    elif 'news' in query:
        response = get_news()

    elif 'play music' in query:
        response = "Music playing feature is only available in desktop mode."

    elif "what do you remember" in query:
        response = query_llm_for_memory(query)

    else:
        response = api_client.models.generate_content(model="gemini-2.0-flash", contents=query).text

    store_conversation(query, response)
    return jsonify({"response": response})


def get_weather(city):
    API_KEY = "0c65b679157351026667ac0e69722100"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)

    try:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = round(data['main']['temp'] - 273.15, 2)
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return f"The weather in {city} is {weather}. Temperature is {temperature}°C with {humidity}% humidity."
    except:
        return "Error fetching weather data!"


def get_news():
    url = "https://gnews.io/api/v4/top-headlines?category=general&country=in&lang=en&max=5&apikey=38d9028d1bd5f745be876a9c416c3489"
    response = requests.get(url)
    data = response.json()

    if "articles" in data:
        return "\n".join([f"{a['source']['name']}: {a['title']}" for a in data["articles"]])
    return "Error fetching news."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
