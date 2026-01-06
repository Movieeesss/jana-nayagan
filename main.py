import time, requests, os, threading, pytz
from flask import Flask
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://in.bookmyshow.com/movies/madurai/jana-nayagan/ET00430817"
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
    
    send_telegram("🚀 *Bot Restarted:* Monitoring Madurai every 5 minutes.")
    while True:
        try:
            driver.get(URL)
            time.sleep(5)
            if "Book tickets" in driver.page_source:
                send_telegram(f"🚨 *TICKETS LIVE!* 🚨\n{URL}")
            print(f"Checked at {datetime.now(IST).strftime('%H:%M:%S')} IST")
            time.sleep(300) # 5 Minutes
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    start_monitoring()
