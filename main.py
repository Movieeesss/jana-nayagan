import time, requests, os, threading, pytz
from flask import Flask
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

app = Flask(__name__)
@app.route('/')
def home(): return "Madurai Jan 9th Detailed Monitor is LIVE"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Specific Madurai URL for January 9, 2026
TARGET_URL = "https://in.bookmyshow.com/movies/madurai/jana-nayagan/buytickets/ET00430817/20260109"
IST = pytz.timezone('Asia/Kolkata')

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def start_monitoring():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    send_telegram("🧐 *Detailed Monitor Active:* Tracking all theaters & showtimes for Jan 9th.")
    
    last_data = {} # To track {TheaterName: [Showtimes]}

    while True:
        try:
            driver.get(TARGET_URL)
            time.sleep(8) # Wait for React content to load
            
            # Find theater containers
            venue_elements = driver.find_elements(By.CLASS_NAME, "list")
            current_data = {}

            for venue in venue_elements:
                try:
                    name = venue.find_element(By.CLASS_NAME, "__venue-name").text
                    # Find all showtimes for this specific theater
                    times = venue.find_elements(By.CLASS_NAME, "showtime-pill")
                    showtimes = [t.text.replace('\n', ' ') for t in times if t.text]
                    if name:
                        current_data[name] = showtimes
                except:
                    continue

            # Check for changes
            if current_data and current_data != last_data:
                msg = "🎭 *THEATER & SHOWTIME UPDATE!*\n\n"
                for theater, times in current_data.items():
                    show_str = ", ".join(times) if times else "No times listed"
                    msg += f"🏛️ *{theater}*\n🕒 {show_str}\n\n"
                
                msg += f"🔗 [Book on BookMyShow]({TARGET_URL})"
                send_telegram(msg)
                last_data = current_data
            
            print(f"Checked at {datetime.now(IST).strftime('%H:%M:%S')} - Theaters found: {len(current_data)}")
            time.sleep(300) # 5 Minutes
            
        except Exception as e:
            print(f"Error during scrape: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    start_monitoring()
