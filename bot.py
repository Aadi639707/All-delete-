import os
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- Flask Server for Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Telegram Bot Logic ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

client = TelegramClient('deleter_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.ChatAction)
async def handler(event):
    # Check if the bot is added as an admin
    if event.new_pin or event.user_added or event.action_message:
        try:
            me = await client.get_me()
            if event.user_id == me.id:
                print(f"Added to {event.chat_id}. Starting mass delete...")
                
                # Delete all messages
                async for msg in client.iter_messages(event.chat_id):
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting: {e}")
                        
                print("All messages deleted successfully.")
        except Exception as e:
            print(f"Critical Error: {e}")

if __name__ == "__main__":
    keep_alive() # Start Flask server
    print("Bot is alive...")
    client.run_until_disconnected()
      
