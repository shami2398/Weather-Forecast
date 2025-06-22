import tkinter as tk
from PIL import Image, ImageTk
import requests
import time
import webbrowser
from geopy.geocoders import Nominatim

class GIFLabel(tk.Label):
    """A Label that displays animated GIFs"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.frames = []
        self.idx = 0
        self.delay = 100  # milliseconds between frames
        self.after_id = None
    
    def load(self, gif_path):
        """Load a GIF and prepare for animation"""
        try:
            img = Image.open(gif_path)
            self.frames = []
            
            # Extract frames from GIF
            for frame in range(0, img.n_frames):
                img.seek(frame)
                self.frames.append(ImageTk.PhotoImage(img.copy()))
            
            self.idx = 0
            self.start_animation()
            print(f"Successfully loaded: {gif_path}")
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.config(image='')
    
    def start_animation(self):
        """Start the animation"""
        if self.frames:
            self.config(image=self.frames[self.idx])
            self.idx = (self.idx + 1) % len(self.frames)
            self.after_id = self.after(self.delay, self.start_animation)
    
    def stop_animation(self):
        """Stop the animation"""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

def open_google_weather(city):
    try:
        # Open Google Weather directly with the city name
        url = f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}"
        webbrowser.open_new_tab(url)
        return True
    except Exception as e:
        print(f"Error opening Google Weather: {e}")
        return False

def getWeather(event=None):
    city = textfield.get()
    if not city:
        label1.config(text="Please enter a city", fg="red")
        for lbl in detail_labels.values():
            lbl.config(text="")
        icon_label.config(image='')
        icon_label.stop_animation()
        return

    # Open Google Weather
    weather_opened = open_google_weather(city)
    if not weather_opened:
        label1.config(text=f"Could not open weather for {city}", fg="red")
        return

    # Get weather data from OpenWeatherMap
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=84c8123a0a9c7e5d23bc6b6ac398e30c"

    try:
        json_data = requests.get(api).json()
        
        if json_data.get("cod") != 200:
            error_msg = json_data.get("message", "City not found")
            label1.config(text=error_msg.capitalize(), fg="red")
            for lbl in detail_labels.values():
                lbl.config(text="")
            icon_label.stop_animation()
            icon_label.config(image='')
            return

        # Extract weather data
        condition = json_data['weather'][0]['main'].title()
        temp = int(json_data['main']['temp'] - 273.15)
        min_temp = int(json_data['main']['temp_min'] - 273.15)
        max_temp = int(json_data['main']['temp_max'] - 273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        sunrise = time.strftime("%I:%M:%S %p", time.gmtime(json_data['sys']['sunrise'] + json_data['timezone'] - 21600))
        sunset = time.strftime("%I:%M:%S %p", time.gmtime(json_data['sys']['sunset'] + json_data['timezone'] - 21600))

        # Update main weather display
        label1.config(text=f"{city}\n{condition}\n{temp}°C", fg="white")

        # Update weather details
        detail_labels["temp"].config(text=f"Temperature: {temp}°C", fg="white")
        detail_labels["max_temp"].config(text=f"Max Temp: {max_temp}°C", fg="orange")
        detail_labels["min_temp"].config(text=f"Min Temp: {min_temp}°C", fg="cyan")
        detail_labels["pressure"].config(text=f"Pressure: {pressure} hPa", fg="yellow")
        detail_labels["humidity"].config(text=f"Humidity: {humidity}%", fg="light blue")
        detail_labels["wind"].config(text=f"Wind Speed: {wind} m/s", fg="white")
        detail_labels["sunrise"].config(text=f"Sunrise: {sunrise}", fg="pink")
        detail_labels["sunset"].config(text=f"Sunset: {sunset}", fg="light green")

        # Weather condition to GIF mapping
        condition_map = {
            "Clear": "clear_sky.gif",
            "Clouds": "cloudy.gif",
            "Rain": "rain.gif",
            "Drizzle": "rain.gif",
            "Thunderstorm": "thunderstorm.gif",
            "Snow": "snow.gif",
            "Mist": "fog.gif",
            "Haze": "fog.gif",
            "Fog": "fog.gif",
            "Smoke": "fog.gif",
            "Dust": "fog.gif",
            "Sand": "fog.gif",
            "Ash": "fog.gif",
            "Squall": "storm.gif",
            "Tornado": "storm.gif"
        }

        # Load appropriate weather icon
        icon_name = condition_map.get(condition, "cloudy.gif")
        try:
            icon_label.stop_animation()
            icon_label.load(icon_name)
        except Exception as e:
            print(f"Error loading animated icon: {e}")
            icon_label.config(image='')

    except Exception as e:
        label1.config(text="Error retrieving data", fg="red")
        for lbl in detail_labels.values():
            lbl.config(text="")
        icon_label.stop_animation()
        icon_label.config(image='')
        print("Error:", e)

# Create main window
canvas = tk.Tk()
canvas.geometry("600x800")
canvas.title("Weather App")
canvas.configure(bg="brown")

# Fonts
f = ("Helvetica", 14)
t = ("Helvetica", 20, "bold")
h = ("Helvetica", 40, "bold")

# Title
title_label = tk.Label(canvas, text="Weather App", font=h, bg="brown", fg="white")
title_label.pack(pady=10)

# Instructions
instructions = tk.Label(canvas, 
                       text="Enter a city name and press Search/Enter.\nGoogle Weather will open with the location,\nthen weather data will appear below.",
                       font=("Helvetica", 12), 
                       bg="brown", 
                       fg="white")
instructions.pack(pady=5)

# Search Frame
search_frame = tk.Frame(canvas, bg="brown")
search_frame.pack(pady=10)

textfield = tk.Entry(search_frame, font=t, width=20, bd=3, relief="groove")
textfield.pack(side=tk.LEFT, padx=5)
textfield.focus()

search_button = tk.Button(search_frame, text="Search", font=f, command=getWeather, 
                         bg="#4CAF50", fg="white", relief="raised")
search_button.pack(side=tk.LEFT, padx=5)

# Display Frame
display_frame = tk.Frame(canvas, bg="brown")
display_frame.pack(pady=20)

# Main weather display
label1 = tk.Label(display_frame, font=t, bg="brown", fg="white")
label1.pack()

# Animated weather icon
icon_label = GIFLabel(display_frame, bg="brown")
icon_label.pack(pady=10)

# Weather details labels
detail_labels = {
    "temp": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "max_temp": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "min_temp": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "pressure": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "humidity": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "wind": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "sunrise": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown"),
    "sunset": tk.Label(display_frame, font=("Helvetica", 16, "bold"), bg="brown")
}

for lbl in detail_labels.values():
    lbl.pack(anchor="w", padx=20)

# Bind Enter key to search
textfield.bind('<Return>', getWeather)

# Start the application
canvas.mainloop()