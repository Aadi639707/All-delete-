import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, types

# --- Render Web Service Port Fix ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))))
    t.daemon = True
    t.start()

# --- Bot Config ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

client = TelegramClient('auto_cleaner', API_ID, API_HASH)

async def delete_all_messages(chat_id):
    print(f"🚀 Cleaning started in: {chat_id}")
    try:
        async for msg in client.iter_messages(chat_id):
            try:
                await msg.delete()
                await asyncio.sleep(0.5) # Flood wait se bachne ke liye thoda delay
            except Exception as e:
                print(f"Skip: {e}")
        print(f"✅ Full Cleanup Done in {chat_id}")
    except Exception as e:
        print(f"Error in {chat_id}: {e}")

# Trigger: Jab bot ko Admin banaya jaye (Channel ya Group dono mein)
@client.on(events.Raw)
async def handler(update):
    # Check if someone added the bot as admin or changed permissions
    if isinstance(update, types.UpdateChannelParticipant):
        me = await client.get_me()
        if update.user_id == me.id:
            # Check if bot is now an Admin
            if isinstance(update.new_participant, (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)):
                await delete_all_messages(update.channel_id)

# Command for Group (Back up option)
@client.on(events.NewMessage(pattern='/delall'))
async def group_manual(event):
    await delete_all_messages(event.chat_id)

async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("🤖 Bot Active: Channel/GC Deleter is Running!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
    
