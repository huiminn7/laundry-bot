import asyncio
from datetime import datetime
from telegram import Bot
from supabase import create_client

# ========== CONFIG ==========
try:
    from config import TOKEN, SUPABASE_URL, SUPABASE_KEY
except ImportError:
    print("❌ Error: config.py not found.")
    exit(1)

bot = Bot(token=TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_reminders():
    print("⏳ Laundry Reminder Engine is online and watching the clock...")
    
    while True:
        try:
            # 1. Get the exact current time
            now = datetime.now().isoformat()
            
            # 2. Ask Supabase: "Give me all reminders where the end_time is right now or in the past"
            response = supabase.table('reminders').select('*').lte('end_time', now).execute()
            expired_reminders = response.data
            
            for reminder in expired_reminders:
                chat_id = reminder['chat_id']
                machine_num = reminder.get('machine_id', 'Unknown')
                
                # 3. Fire the push notification to Telegram!
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"🔔 *BEEP BEEP!*\n\nYour laundry in Washer {machine_num} is finished!\n\nPlease collect your clothes so others can use the machine.",
                        parse_mode="Markdown"
                    )
                    print(f"✅ Successfully notified @{reminder.get('username')}")
                except Exception as e:
                    print(f"❌ Failed to text chat_id {chat_id}: {e}")
                
                # 4. Delete the reminder from the database so we don't spam them forever
                supabase.table('reminders').delete().eq('id', reminder['id']).execute()
                
        except Exception as e:
            print(f"⚠️ Warning in background loop: {e}")
            
        # Wait exactly 60 seconds before checking the clock again
        await asyncio.sleep(60)

if __name__ == "__main__":
    # Start the infinite background loop
    asyncio.run(check_reminders())