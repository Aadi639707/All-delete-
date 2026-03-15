import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- Flask Server for Render (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render automatically assigns a PORT, default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- Telegram Bot Configuration ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize Client
client = TelegramClient('deleter_session', API_ID, API_HASH)

@client.on(events.ChatAction)
async def handler(event):
    # Check if the bot was added to a group or channel
    if event.user_added or event.created or event.action_message:
        me = await client.get_me()
        if event.user_id == me.id:
            print(f"✅ Added to Chat ID: {event.chat_id}. Cleaning started...")
            
            try:
                # Optimized message deletion
                async for msg in client.iter_messages(event.chat_id):
                    try:
                        await msg.delete()
                    except Exception as e:
                        # Log errors like FloodWait or lack of permission
                        print(f"⚠️ Could not delete message: {e}")
                print("🎯 Cleanup complete.")
            except Exception as e:
                print(f"❌ Critical Error during deletion: {e}")

async def main():
    # Start the bot properly with awaiting
    await client.start(bot_token=BOT_TOKEN)
    print("🤖 Bot is successfully logged in and monitoring...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    keep_alive()  # Start Flask in a background thread
    
    # Modern way to run the async event loop without RuntimeError
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
