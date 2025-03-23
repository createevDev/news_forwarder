from telethon.sync import TelegramClient, events
import openai
import tweepy
import os
from dotenv import load_dotenv

# Ubah lokasi file .env dari venv/.env ke .env (root project)
load_dotenv()

# Tambahkan setelah load_dotenv()
print("Checking environment variables:")
print(f"TELEGRAM_API_ID: {os.getenv('TELEGRAM_API_ID')}")
print(f"TELEGRAM_API_HASH: {os.getenv('TELEGRAM_API_HASH')}")

API_ID = os.getenv("TELEGRAM_API_ID")  # API ID dari Telegram
API_HASH = os.getenv("TELEGRAM_API_HASH")  # API Hash dari Telegram
CHANNEL_USERNAME = "risalahamar"  # Ganti dengan username channel (tanpa @)

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Periksa apakah semua variabel lingkungan diperlukan telah dimuat
required_vars = {
    "API_ID": API_ID, 
    "API_HASH": API_HASH,
    "TWITTER_API_KEY": TWITTER_API_KEY,
    "TWITTER_API_SECRET": TWITTER_API_SECRET,
    "TWITTER_ACCESS_TOKEN": TWITTER_ACCESS_TOKEN,
    "TWITTER_ACCESS_SECRET": TWITTER_ACCESS_SECRET,
    "OPENAI_API_KEY": OPENAI_API_KEY
}

missing_vars = [var for var, val in required_vars.items() if val is None]
if missing_vars:
    raise EnvironmentError(f"Variabel lingkungan berikut tidak ditemukan: {', '.join(missing_vars)}")

# Buat session Telethon dengan akun Telegram pribadi
client = TelegramClient("user_session", API_ID, API_HASH)

async def process_message(event):
    message_text = event.message.text

    if message_text:  # Pastikan pesan tidak kosong
        print(f"Pesan baru dari Telegram: {message_text}")
        
        # Poles teks dengan ChatGPT
        client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)
        polishing_prompt = "terdapat dua bahasa pada teks di atas, arab dan indonesia. Terjemahkan teks berbahasa indonesia menjadi inggris dengan gaya bahasa jurnalisme"
        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"{message_text} : {polishing_prompt}"}]
        )
        polished_text = response.choices[0].message.content

        # Posting ke X (Twitter)
        post_to_x(polished_text)

# Fungsi posting ke X (Twitter)
def post_to_x(text):
    try:
        # Batasi teks untuk Twitter (280 karakter)
        if len(text) > 280:
            text = text[:277] + "..."
            
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        client.create_tweet(text=text)
        print(f"✅ Tweet terkirim: {text}")
    except Exception as e:
        print(f"Error saat posting ke Twitter: {e}")

# Event handler untuk membaca pesan baru dari channel
@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):
    await process_message(event)

print("✅ Bot mulai berjalan...")
client.start()
client.run_until_disconnected()
