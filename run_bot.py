# run_bot.py
import time
from datetime import datetime, timedelta
import requests
import config
from alert_handler import AlertHandler
from tg_bot_service import TelegramBotService

# Настройки
SYMBOLS = config.SYMBOLS  # список монет, які сконфігуровані
INTERVAL = config.INTERVAL  # '1m'
N = config.AVG_PERIODS  # кількість попередніх обʼємів
MULTIPLIER = config.MULTIPLIER  # 10

BOT = TelegramBotService(config.TELEGRAM_TOKEN, config.CHAT_ID)

def get_binance_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={N+1}"
    r = requests.get(url, timeout=10)
    return r.json() if r.status_code == 200 else []

def calculate_avg_vol(volumes):
    return sum(volumes) / len(volumes) if volumes else 0

def monitor():
    while True:
        for sym in SYMBOLS:
            klines = get_binance_klines(sym)
            if len(klines) < N + 1:
                continue
            vols = [float(k[5]) for k in klines]
            avg_vol = calculate_avg_vol(vols[:-1])
            last_vol = vols[-1]
            if avg_vol > 0 and last_vol >= avg_vol * MULTIPLIER:
                text = (
                    f"📊 Обʼємний сплеск!\n"
                    f"Пара: {sym}\n"
                    f"Інтервал: {INTERVAL}\n"
                    f"Середній обʼєм ({N}): {avg_vol:.2f}\n"
                    f"Новий обʼєм: {last_vol:.2f}\n"
                    f"Кратність: {last_vol/avg_vol:.2f}×"
                )
                BOT.send_message(text)
        time.sleep(60)

if __name__ == "__main__": 
    monitor()
