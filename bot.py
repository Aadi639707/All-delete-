import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# --- Render Port Binding (Fake Server) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Active"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))))
    t.daemon = True
    t.start()

# --- Bot Configuration ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

client = TelegramClient('debug_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/cleanup'))
async def manual_id_cleanup(event):
    # Check if message is in DM
    if not event.is_private:
        return

    try:
        # Command format: /cleanup -100123456789
        parts = event.text.split(" ")
        if len(parts) < 2:
            await event.reply("❌ Format galat hai! Use karein: `/cleanup -100xxxxxxxxxx`")
            return

        target_chat = int(parts[1])
        status_msg = await event.reply(f"🔍 Checking access for ID: {target_chat}...")

        # Count total messages first to see if it's working
        messages = []
        async for msg in client.iter_messages(target_chat, limit=100):
            messages.append(msg)
        
        if not messages:
            await status_msg.edit("ℹ️ Is ID par koi messages nahi mile ya bot admin nahi hai.")
            return

        await status_msg.edit(f"🗑️ Deletion shuru ho raha hai {target_chat} mein...")

        count = 0
        async for msg in client.iter_messages(target_chat):
            try:
                await msg.delete()
                count += 1
                if count % 10 == 0:
                    print(f"Deleted {count} messages in {target_chat}")
            except FloodWaitError as e:
                print(f"Waiting for {e.seconds} seconds due to FloodWait...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Error deleting message: {e}")
                continue

        await event.reply(f"✅ Kaam poora hua! Total {count} messages delete kiye gaye.")

    except ValueError:
        await event.reply("❌ Invalid ID! Channel ID hamesha -100 se shuru hoti hai.")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        print(f"LOG ERROR: {e}")

async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("🤖 Debug Bot started. Send ID in DM to cleanup.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
    
