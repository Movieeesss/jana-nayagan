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
def home(): return "Trichy 24/7 Monitor is Active"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Trichy URL for Jana Nayagan
TRICHY_URL = "https://in.bookmyshow.com/movies/trichy/jana-nayagan/ET00430817"
IST = pytz.timezone('Asia/Kolkata')

def send_telegram(msg):
    # Sends a formatted Markdown message to Telegram
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def start_monitoring():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    send_telegram("🚀 *Trichy Monitor Started*\nChecking for new theaters every 5 minutes.")
    
    last_theater_data = {} # Stores {TheaterName: [Showtimes]}

    while True:
        try:
            driver.get(TRICHY_URL)
            time.sleep(10) # Wait for theaters to load
            
            # Find theater containers on BookMyShow
            venues = driver.find_elements(By.CLASS_NAME, "list")
            current_data = {}

            for venue in venues:
                try:
                    name = venue.find_element(By.CLASS_NAME, "__venue-name").text
                    times = venue.find_elements(By.CLASS_NAME, "showtime-pill")
                    showtimes = [t.text.replace('\n', ' ') for t in times if t.text]
                    if name:
                        current_data[name] = showtimes
                except:
                    continue

            ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

            # 1. Check for NEW theaters or CHANGED showtimes
            if current_data and current_data != last_theater_data:
                msg = f"🤖 *Jana Nayagan Trichy Update*\n"
                msg += f"🕒 IST: {ist_now}\n\n"
                
                for theater, times in current_data.items():
                    show_str = ", ".join(times) if times else "Bookings Opening Soon"
                    msg += f"🏛️ *{theater}*\n✅ {show_str}\n\n"
                
                msg += f"🔗 [Book Now]({TRICHY_URL})"
                send_telegram(msg)
                last_theater_data = current_data
            
            # 2. Hourly Status Check (Like your image)
            print(f"[{ist_now}] Checked Trichy. Theaters found: {len(current_data)}")
            
            time.sleep(300) # Wait exactly 5 minutes
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    start_monitoring()
