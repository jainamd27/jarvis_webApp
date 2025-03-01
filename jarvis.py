import time
import sys
import json
import os
import keyboard
import datetime
import requests
import pyttsx3
import speech_recognition as sr
from google import genai

# Initialize API Client
api_client = genai.Client(api_key="AIzaSyAAQB7cXM63W2KV7Xz7maEpBJAWm4Y4b6Q")

# Memory File
memory_file = "memory.json"


def load_memory():
    try:
        with open(memory_file, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "history" not in data:
                return {"history": []}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"history": []}


conversations = load_memory()


def save_memory(conversations):
    with open(memory_file, "w") as f:
        json.dump(conversations, f, indent=4)


def store_conversation(user_query, jarvis_response):
    conversations["history"].append({
        "user": user_query,
        "jarvis": jarvis_response
    })
    save_memory(conversations)


# Text-to-Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def say(text):
    engine.say(text)
    print("Jarvis:", text)
    engine.runAndWait()


def greetings():
    curr_time = datetime.datetime.now().hour
    if 6 <= curr_time < 12:
        say("Good Morning, Sir")
    elif 12 <= curr_time < 18:
        say("Good Afternoon, Sir")
    elif 18 <= curr_time < 22:
        say("Good Evening, Sir")
    else:
        say("Good Night, Sir, it's too late, you need to take a rest now")


def takeCommand():
    with sr.Microphone() as source:
        say("Listening...")
        r = sr.Recognizer()
        audio_data = r.listen(source)
        try:
            say("Recognizing...")
            query = r.recognize_google(audio_data)
            print("You:", query)
            return query.lower()
        except Exception:
            say("I couldn't get it, say that again please!")
            inp = input("Enter your command by typing: ")
            return inp.lower() if inp else None


def query_llm_for_memory(user_query):
    memory_text = "\n".join([f"User: {conv['user']}\nJarvis: {conv['jarvis']}" for conv in conversations["history"]])

    prompt = f"""
    You are an AI assistant named Jarvis. You have access to past conversations with the user.

    Here is the conversation history:
    {memory_text}

    Now, the user asks: "{user_query}"

    If the user's question is about something in the history, extract the relevant memory and answer naturally. 
    If you don't have the answer, say you don't remember.
    """

    response = api_client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text
    return response


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

        weather_summary = f"The weather in {city} is {weather}. The temperature is {temperature}°C with {humidity}% humidity and wind speed of {wind_speed} m/s."
        return weather_summary
    except Exception:
        say("Error fetching weather data!")
        return "Error"


def get_news():
    url = "https://gnews.io/api/v4/top-headlines?category=general&country=in&lang=en&max=5&apikey=38d9028d1bd5f745be876a9c416c3489"
    response = requests.get(url)
    data = response.json()

    if "articles" in data:
        for article in data["articles"]:
            say(f"Source: {article['source']['name']}, Title: {article['title']}")
            print(f"URL: {article['url']}\n")
    else:
        say("Error fetching news.")


def taskExe(query):
    response = ""

    if 'weather' in query:
        say("Tell me your city name")
        city = takeCommand()
        if city:
            response = get_weather(city)
            say(response)

    elif 'top headlines' in query or 'news' in query:
        get_news()

    elif 'play music' in query:
        os.startfile("C:\\Users\\JAINAM\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe")
        time.sleep(1)
        keyboard.press_and_release("space")
        say("Okay sir, enjoy it!")

    elif 'pause music' in query:
        os.startfile("C:\\Users\\JAINAM\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe")
        time.sleep(1)
        keyboard.press_and_release("space")
        say("Roger that!")

    elif 'open photoshop' in query:
        os.startfile("C:\\Users\\JAINAM\\Desktop\\Adobe Photoshop 2025.lnk")

    elif 'bye' in query or 'goodbye' in query:
        say("Okay sir, Have a nice day, you can call me anytime!")
        sys.exit()

    elif "what do you remember" in query or "what is my" in query or "when is my" in query or "what's my" in query or "who is" in query or "when was" in query or "who I am" in query or "who I'm":
        response = query_llm_for_memory(query)
        say(response)

    else:
        response = api_client.models.generate_content(model="gemini-2.0-flash", contents=query).text
        say(response)

    store_conversation(query, response)


if __name__ == "__main__":
    say("Hello sir, I'm Jarvis, rebooted!")
    greetings()
    say("How can I help you, Jainam?")

    while True:
        query = takeCommand()
        if query:
            taskExe(query)
